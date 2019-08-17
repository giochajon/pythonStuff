import Queue
import threading
import time
import urllib2

my_sites = [
    'http://www.imdb.com',
    'http://www.rottentomatoes.com'
    ]

# Create a queue for our processing
queue = Queue.Queue()


class MyThread(threading.Thread):
  """Create a thread to make the url call."""

  def __init__(self, queue):
    super(MyThread, self).__init__()
    self.queue = queue

  def run(self):
    while True:
      # Grab a url from our queue and make the call.
      my_site = self.queue.get()
      url = urllib2.urlopen(my_site)

      # Grab a little data to make sure it is working
      print (url.read(1024))

      # Send the signal to indicate the task has completed
      self.queue.task_done()


def main():

  # This will create a 'pool' of threads to use in our calls
  for _ in range(4):
    t = MyThread(queue)

    # A daemon thread runs but does not block our main function from exiting
    t.setDaemon(True)

    # Start the thread
    t.start()

  # Now go through our site list and add each url to the queue
  for site in my_sites:
    queue.put(site)

  # join() ensures that we wait until our queue is empty before exiting
  queue.join()

if __name__ == '__main__':
  start = time.time()
  main()
  print ('Total Time: {0}'.format(time.time() - start))
