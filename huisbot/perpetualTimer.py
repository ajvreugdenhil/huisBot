from threading import Timer, Thread, Event

class perpetualTimer():
   def __init__(self,t,method):
      self.t=t
      self.method = method
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.method()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
