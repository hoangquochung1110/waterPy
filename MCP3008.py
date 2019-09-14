import RPi.GPIO as GPIO
import time
import math
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
CLK  = 18
DOUT = 23
DIN  = 24
CS   = 25


GPIO.setup(CLK,  GPIO.OUT)
GPIO.setup(DOUT, GPIO.IN)
GPIO.setup(DIN,  GPIO.OUT)
GPIO.setup(CS,   GPIO.OUT)

potentiometer = 0

# read SPI data from MCP3008 chip, 8 possible adc's  
def readadc(num, clk, dout, din, cs):
  if ((num > 7) or (num < 0)):
    return -1

  GPIO.output(cs , 1) # Stopping any previous transitions
  GPIO.output(clk, 0) # start clock
  GPIO.output(cs , 0) # Selecting slave to start transition

  command = num 
  command |= 0x18     # Puting 2 ones at front of the number
  command <<= 3       # Moving the number to the first 5 digits

  for i in range(5):
    if (command & 0x80):
	    GPIO.output(din, 1)
    else:
	    GPIO.output(din, 0)
	    
    command <<= 1
    GPIO.output(clk, 1) # clock pulse to shift
    GPIO.output(clk, 0)
  
  out = 0
  # read in one empty bit, 10 ADC bits and one 'null' bit at the end
  for i in range(12):
    GPIO.output(clk, 1) # clock pulse to shift
    GPIO.output(clk, 0)
    out <<=1
    out |= GPIO.input(dout)

  GPIO.output(cs , 1) # Deselecting slave to stop transmition
  out >>= 1
  out = 100-(out/1023.0)*100
  out = math.ceil(out)
  return out	 
		
if __name__ == "__main__":
  try:
    while True:
      value = readadc(potentiometer, CLK, DOUT, DIN, CS)
      print(value)
      print ("*************")
      time.sleep(1)
  except KeyboardInterrupt:
    GPIO.cleanup()
