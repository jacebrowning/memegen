from webargs import core
from webargs.flaskparser import FlaskParser

parser = FlaskParser(('form', 'data'))


@parser.location_handler('data')
def parse_data(request, name, field):
    return core.get_value(request.data, name, field)
