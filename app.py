import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/color/(.*)',tornado.web.StaticFileHandler, {'path': './web/color'}),
        (r'/css/(.*)',tornado.web.StaticFileHandler, {'path': './web/css'}),
        (r'/font-awesome/(.*)',tornado.web.StaticFileHandler, {'path': './web/font-awesome'}),
        (r'/fonts/(.*)',tornado.web.StaticFileHandler, {'path': './web/fonts'}),
        (r'/img/(.*)',tornado.web.StaticFileHandler, {'path': './web/img'}),
        (r'/js/(.*)',tornado.web.StaticFileHandler, {'path': './web/js'}),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()