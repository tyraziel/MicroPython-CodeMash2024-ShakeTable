# Various code snippets taken from https://github.com/javaplus/PicoProjects/ and modified
# My code modifications released under the MIT License (c) 2024 Andrew Potozniak (Tyraziel)

import time

from machine import Pin, ADC
import sg90
import utime
import tm1637

time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico!")


version = "1"
# initialize the signal Pin
sg90.servo_pin(15)

display = tm1637.TM1637(clk=Pin(1), dio=Pin(0))

button = Pin(17, Pin.IN, Pin.PULL_DOWN)

# debounce utime saying 500ms between button presses
DEBOUNCE_utime = 250 #acp playing around with debounce time
# debounce counter is our counter from the last button press
# initialize to current utime
debounce_counter = utime.ticks_ms()

# define flag to say when button is pressed:
button_pressed = False
table_on = False

# define function to be called when button is pressed
def button_interrupt_handler(pin):
    # since this is called by an interrupt do very little
    # need to give control back to CPU quickly.
    # Could possibly do debounce work here???
    global button_pressed
    button_pressed = True

## define interrupt to call our function when button is pressed:
button.irq(trigger=Pin.IRQ_RISING, handler=button_interrupt_handler)    

# Function to handle turning LED off and on and setting flag
def toggle_table():
    global table_on
    if(table_on):
        table_on = False
    else:
        table_on = True

# Function to handle when the button is pressed
def button_press_detected():
    global debounce_counter, button_pressed
    current_utime = utime.ticks_ms()
    # Calculate utime passed since last button press
    utime_passed = utime.ticks_diff(current_utime,debounce_counter)
    print("utime passed=" + str(utime_passed))
    if (utime_passed > DEBOUNCE_utime):
        print("Button Pressed!")
        # set debounce_counter to current utime
        debounce_counter = utime.ticks_ms()
        toggle_table()
        button_pressed=False
    
    else:
        button_pressed = False
        print("Not enough utime")


msWaitArray = [300, 200, 125]
startingTimeLeftToShakeArray = [2500, 2500, 2500] #10000
#closer to 90 means less movement
rightDegArray = [75, 75, 75] #45
leftDegArray = [105, 105, 105] #135

#Center
#shake at 300ms sleep for 10 seconds (10000ms)
#reset
sg90.move_to(90)
display.show("STRT", colon=False)

while True:

    if button_pressed==True:
        button_press_detected()

    if table_on==True:
        for i in range(0, len(msWaitArray)):
            timeLeftToShake = startingTimeLeftToShakeArray[i]#10000
            msToWait = msWaitArray[i]#300 - (i * 100)
            shakeNumber = i + 1
            rightDeg = rightDegArray[i]
            leftDeg = leftDegArray[i]
            
            while timeLeftToShake > 0 and table_on:
                if button_pressed==True:
                    button_press_detected()
                else:    
                    #display.show(" 1" + str(int(timeLeftToShake / 1000)))
                    display.numbers(shakeNumber, int(timeLeftToShake / 1000), colon=False)
                    sg90.move_to(rightDeg)
                    utime.sleep_ms(msToWait)
                    timeLeftToShake = timeLeftToShake - msToWait
                    display.numbers(shakeNumber, int(timeLeftToShake / 1000), colon=False)
                    sg90.move_to(leftDeg)
                    #display.numbers(0, 50, colon=False)
                    utime.sleep_ms(msToWait)
                    timeLeftToShake = timeLeftToShake - msToWait
                    display.numbers(shakeNumber, int(timeLeftToShake / 1000), colon=False)
            if i == len(msWaitArray) - 1:
                table_on = False

    #Center
    sg90.move_to(90)
    display.show("RDY"+str(version), colon=False)
