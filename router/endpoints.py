from app import Application

application = Application('192.168.0.115', 80)


def render_path(path: str) -> str:
    with open(path, 'r') as text:
        return text.read()


@application.router.arr_route('GET', '/static')
def static(request, headers):
    return render_path(f'html_files/{request.URI[8:]}')


@application.router.route('GET', '/')
def main(request, headers):
    return render_path('html_files/index.html')


@application.router.route('GET', '/static/style.css')
def css(request, headers):
    headers['Content-Type'] = 'text/css'
    return render_path('html_files/style.css')


@application.router.route('GET', '/style.css')
def css(request, headers):
    headers['Content-Type'] = 'text/css'
    return render_path('html_files/style.css')


@application.router.route('POST', '/')
def receive(request, headers):
    print('receive')
    return 'Message received'


application.run()

