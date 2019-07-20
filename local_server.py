from webappsunscene import app
import logging

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

exp_logger = logging.getLogger("experiments")
exp_logger.addHandler(handler)
exp_logger.setLevel(logging.DEBUG)

app.logger.debug("Starting")
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='0.0.0.0', port=5002, threaded=True, debug=True)
