import logging

import uvicorn


log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

if __name__ == "__main__":
    logging.info("Application Point RUN")
    uvicorn.run(
        "point.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_config=log_config,
        app_dir="../../src"
    )
