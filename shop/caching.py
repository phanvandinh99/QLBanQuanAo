"""
Caching utilities for performance optimization
"""

try:
    from flask_caching import Cache
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    print("⚠️ Flask-Caching not available, caching disabled")

import functools
import time

# Initialize cache if available
if CACHING_AVAILABLE:
    cache = Cache()
else:
    cache = None

def init_cache(app):
    """Initialize cache for the Flask app"""
    if CACHING_AVAILABLE and cache:
        cache.init_app(app, config={
            'CACHE_TYPE': 'simple',  # Use 'redis' in production
            'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default
        })
    else:
        print("ℹ️ Caching disabled - Flask-Caching not available")

def cached(timeout=None):
    """Decorator for caching function results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHING_AVAILABLE or not cache:
                # If caching not available, just execute the function
                return func(*args, **kwargs)

            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)

            # Try to get from cache first
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result

        # Add cache clearing method
        def clear_cache():
            if CACHING_AVAILABLE and cache:
                try:
                    cache.delete_many([
                        key for key in (cache.cache._cache.keys() if hasattr(cache.cache, '_cache') else [])
                        if key.startswith(func.__name__)
                    ])
                except:
                    pass  # Ignore cache clearing errors

        wrapper.clear_cache = clear_cache
        return wrapper
    return decorator

def cache_key_prefix(prefix):
    """Decorator to add prefix to cache keys"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            original_key = functools._make_key(args, kwargs, typed=False)
            prefixed_key = f"{prefix}:{original_key}"
            return func(*args, **kwargs, _cache_key=prefixed_key)
        return wrapper
    return decorator

class CacheManager:
    """Cache manager for common operations"""

    @staticmethod
    def get_categories():
        """Get cached categories"""
        @cached(timeout=600)  # 10 minutes
        def _get_categories():
            from shop.utilities import get_categories
            return get_categories()
        return _get_categories()

    @staticmethod
    def get_brands():
        """Get cached brands"""
        @cached(timeout=600)  # 10 minutes
        def _get_brands():
            from shop.utilities import get_brands
            return get_brands()
        return _get_brands()

    @staticmethod
    def get_popular_products(limit=8):
        """Get cached popular products"""
        @cached(timeout=300)  # 5 minutes
        def _get_popular_products(limit):
            from shop.utilities import get_popular_products
            return get_popular_products(limit)
        return _get_popular_products(limit)

    @staticmethod
    def get_product_ratings():
        """Get cached product ratings"""
        @cached(timeout=300)  # 5 minutes
        def _get_product_ratings():
            from shop.utilities import get_product_ratings
            return get_product_ratings()
        return _get_product_ratings()

    @staticmethod
    def clear_product_cache():
        """Clear all product-related cache"""
        if CACHING_AVAILABLE and cache:
            try:
                cache.delete_many([
                    key for key in (cache.cache._cache.keys() if hasattr(cache.cache, '_cache') else [])
                    if any(prefix in key for prefix in ['get_popular_products', 'get_product_ratings'])
                ])
            except:
                pass  # Ignore cache clearing errors

    @staticmethod
    def clear_category_cache():
        """Clear category and brand cache"""
        if CACHING_AVAILABLE and cache:
            try:
                cache.delete_many([
                    key for key in (cache.cache._cache.keys() if hasattr(cache.cache, '_cache') else [])
                    if any(prefix in key for prefix in ['get_categories', 'get_brands'])
                ])
            except:
                pass  # Ignore cache clearing errors

def invalidate_cache_on_change(model_class):
    """Decorator to invalidate cache when model changes"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Clear relevant caches based on model (only if caching is available)
            if CACHING_AVAILABLE and cache:
                if model_class.__name__ == 'Product':
                    CacheManager.clear_product_cache()
                elif model_class.__name__ in ['Category', 'Brand']:
                    CacheManager.clear_category_cache()

            return result
        return wrapper
    return decorator

def timed_cache(timeout=300):
    """Cache with timing information for debugging"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Create cache key
            key_parts = [f"{func.__name__}_timed"]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)

            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                print(".4f")
                return result

            # Execute function
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Cache result
            cache.set(cache_key, result, timeout=timeout)

            print(".4f")
            return result

        return wrapper
    return decorator
