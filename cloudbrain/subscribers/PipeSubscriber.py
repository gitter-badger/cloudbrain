import json
import sys
from cloudbrain.subscribers.SubscriberInterface import Subscriber


class PipeSubscriber(Subscriber):
  
  def __init__(self, device_name, device_id, metric_name, pipe_name=None):
    super(PipeSubscriber, self).__init__(device_name, device_id, None)
    self.metric_name = metric_name
    self.pipe_name = pipe_name
    
    
  def connect(self):
    if self.pipe_name is None:
      self.pipe = sys.stdin
    else:
      self.pipe = open(self.pipe_name, 'r')

  def disconnect(self):
    self.pipe.close()
    
    
  
  def consume_messages(self, callback):
    """
    Consume messages emitted by the producer.
    :param callback: callback function called when consuming a message. Need 
    to take 4 arguments: ch, method, properties, body
    """
    
    while True:
      line = self.pipe.readline()
      if line == '':
        return # EOF

      data = json.loads(line)
      body = data['body']
      callback(None, None, None, json.dumps(body))
    
  def get_one_message(self):
    line = self.pipe.readline()
    return json.loads(line)
