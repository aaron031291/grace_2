# Sentry error tracking  
try:  
    import sentry_sdk  
    from sentry_sdk.integrations.logging import LoggingIntegration  
    from sentry_sdk.integrations.fastapi import FastAPIIntegration  
ECHO is on.
    sentry_dsn = os.getenv("SENTRY_DSN")  
    if sentry_dsn:  
        sentry_sdk.init(  
            dsn=sentry_dsn,  
            integrations=[  
                FastAPIIntegration(),  
                LoggingIntegration(  
                    level=logging.INFO,  
                    event_level=logging.ERROR  
                ),  
            ],  
            environment=os.getenv("ENVIRONMENT", "development"),  
            traces_sample_rate=0.1,  
            send_default_pii=False  
        )  
        SENTRY_AVAILABLE = True  
        print("V Sentry error tracking enabled")  
    else:  
        SENTRY_AVAILABLE = False  
        print("? Sentry DSN not configured")  
except ImportError:  
    SENTRY_AVAILABLE = False  
    print("? Sentry SDK not available")  
 
