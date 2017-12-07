ArduinoYun DA for IoTtalk v2
============================

To use this code, only ``custom.py`` needs to be modified.
This code uses device model ``MCU\_board`` as an example, that is, the IDFs/ODFs are

.. code-block:: python

    def odf():  # int only

        return [
          ('D2', 0, 'D2'),     #ODF_name, dimension, Variable_name in Bridge
          ('D3', 0, 'D3'),
          ('D4', 0, 'D4'),
          ('D5~PWM', 0, 'D5~PWM'),
          ('D6~PWM', 0, 'D6~PWM'),
          ('D7', 0, 'D7'),
          ('D8', 0, 'D8'),
          ('D9~PWM', 0, 'D9~PWM'),
        ]

.. code-block:: python

    def idf():

        return [
           ('A0', int),        #IDF_name, Variable_type
           ('A1', int),
           ('A2', int),
           ('A3', int),
           ('A4', int),
           ('A5', int),
         ]
