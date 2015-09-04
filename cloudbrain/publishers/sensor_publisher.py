import argparse

from cloudbrain.publishers.PikaPublisher import PikaPublisher
from cloudbrain.publishers.PipePublisher import PipePublisher
from cloudbrain.utils.metadata_info import get_metrics_names, get_supported_devices
from cloudbrain.settings import RABBITMQ_ADDRESS, MOCK_DEVICE_ID

_SUPPORTED_DEVICES = get_supported_devices()


def parse_args():
  parser = argparse.ArgumentParser()

  parser.add_argument('-i', '--device_id', required=True,
                      help="A unique ID to identify the device you are sending data from. "
                           "For example: 'octopicorn2015'")
  parser.add_argument('-m', '--mock', action='store_true', required=False,
                      help="Use this flag to generate mock data for a "
                           "supported device name %s" % _SUPPORTED_DEVICES)
  parser.add_argument('-n', '--device_name', required=True,
                      help="The name of the device your are sending data from. "
                           "Supported devices are: %s" % _SUPPORTED_DEVICES)
  parser.add_argument('-c', '--cloudbrain', default=RABBITMQ_ADDRESS,
                      help="The address of the CloudBrain instance you are sending data to, for pika publisher.\n"
                           "Use " + RABBITMQ_ADDRESS + " to send data to our hosted service. \n"
                           "Otherwise use 'localhost' if running CloudBrain locally")
  parser.add_argument('-o', '--output', default=None,
                      help="The named pipe you are sending data to (e.g. /tmp/eeg_pipe), for pipe publisher.\n"
                           "The publisher will create the pipe.\n"
                           "By default this is the standard output.")

  parser.add_argument('-b', '--buffer_size', default=10,
                      help='Size of the buffer ')
  parser.add_argument('-p', '--device_port', help="Port used for OpenBCI Device.")

  parser.add_argument('-P', '--publisher', default="pika",
                      help="The subscriber to use to get the data.\n"
                      "Possible options are pika, pipe.\n"
                      "The default is pika.")


  opts = parser.parse_args()
  if opts.device_name == "openbci" and opts.device_port is not None:
    parser.error("You have to specify a port for the OpenBCI device!")
  return opts


def main():
  opts = parse_args()
  mock_data_enabled = opts.mock
  device_name = opts.device_name
  device_id = opts.device_id
  cloudbrain_address = opts.cloudbrain
  buffer_size = opts.buffer_size
  device_port = opts.device_port
  pipe_name = opts.output
  publisher = opts.publisher

  run(device_name,
      mock_data_enabled,
      device_id,
      cloudbrain_address,
      buffer_size,
      device_port,
      pipe_name,
      publisher)


def run(device_name='muse',
        mock_data_enabled=True,
        device_id=MOCK_DEVICE_ID,
        cloudbrain_address=RABBITMQ_ADDRESS,
        buffer_size=10,
        device_port='/dev/tty.OpenBCI-DN0094CZ',
        pipe_name=None,
        publisher_type="pika"):
  if device_name == 'muse':
    from cloudbrain.connectors.MuseConnector import MuseConnector as Connector
  elif device_name == 'openbci':
    from cloudbrain.connectors.OpenBCIConnector import OpenBCIConnector as Connector
  else:
    raise ValueError("Device type '%s' not supported. Supported devices are:%s" % (device_name, _SUPPORTED_DEVICES))

  if mock_data_enabled:
    from cloudbrain.connectors.MockConnector import MockConnector as Connector

  
  if publisher_type not in ['pika', 'pipe']:
    raise ValueError("'%s' is not a valid publisher type. Valid types are %s." % (publisher_type, "pika, pipe"))

  metrics = get_metrics_names(device_name)

  if publisher_type == 'pika':
    publishers = {metric: PikaPublisher(device_name, device_id, cloudbrain_address, metric) for metric in metrics}
  elif publisher_type == 'pipe':
    publishers = {metric: PipePublisher(device_name, device_id, metric, pipe_name) for metric in metrics} 

  for publisher in publishers.values():
    publisher.connect()
  if device_name == 'openbci':
    connector = Connector(publishers, buffer_size, device_name, device_port)
  else:
    connector = Connector(publishers, buffer_size, device_name)
  connector.connect_device()

  if mock_data_enabled and (publisher_type != 'pipe'):
    print "INFO: Mock data enabled."

  if publisher_type == 'pika':
    print ("SUCCESS: device '%s' connected with ID '%s'\n"
           "Sending data to cloudbrain at address '%s' ...") % (device_name,
                                                                device_id,
                                                                cloudbrain_address)
  connector.start()

if __name__ == "__main__":
  main()
  #run('muse', False, 'marion', RABBITMQ_ADDRESS)



