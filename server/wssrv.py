#-*- coding:shift-jis -*-
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
import json

from tornado.options import define, options, parse_command_line

define("port", default = 8080, help = "run on the given port", type = int)

connections = []

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
		self.render('index.html', port=self.application.port)

class rooms(object):
    def __init__(self, *args, **kwargs):
        self.connections = []

    def add_connection(self,obj):
        if not (obj in self.connections): 
            self.connections.append(self)

    def del_connection(self,obj):
        if obj in connections:
            connections.remove(self)

class SocketHandler(tornado.websocket.WebSocketHandler):
#index.htmlでコネクションが確保されると呼び出される
    def open(self):
        print "WebSocket opened"
        self.application.add_connection(self)

    def add_connection(self):
        if not (self in connections): 
            connections.append(self)
    def wait_message(self):
        self.receive_message(self.on_message)

    def on_message(self, message):
        for con in connections:
          try:
            con.write_message(json.dump(message))
          except:
            connections.remove(con)
        self.wait_message()


    #ページが閉じ、コネクションが切れる事で呼び出し
    def on_connection_close(self):
        self.del_connection()
        self.close()

    def del_connection(self):
        if self in connections:
            connections.remove(self)
	  
class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", MainHandler),
      (r"/ws",SocketHandler),
      ]
    settings = dict(
      debug=True,
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      )
    tornado.web.Application.__init__(self, handlers, **settings)

def main():  tornado.options.parse_command_line()  http_server = tornado.httpserver.HTTPServer(Application())  http_server.listen(8888)  tornado.ioloop.IOLoop.instance().start()if __name__ == "__main__":  main()