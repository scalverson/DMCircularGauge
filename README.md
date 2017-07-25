# DMCircularGauge

## Synopsis
This code generates a QWidget subclass in the form of a circular gauge (think speedometer).  Widget is fully scalable
 and accepts inputs for a EPICS "PV" (process variable) from which to retrieve a set of parameters as well as 
 independent max and min range variables.  Intended for use as part of the PyDM package with PyEPICS.  
 
 Values retrieved and used from PV are as follows:  
 
 1. value - current value of the PV (.VAL)
 2. hopr - High Operational limit (.HOPR)
    * Upper control limit of PV
    * Used for max range of gauge if no limit provided to init
 3. lopr - Low Operational limit (.LOPR)
    * Lower control limit of PV
    * Used for min range of gauge if no limit provided to init
 4. hihi - High High alarm limit (.HIHI)
    * Presents as red bar on high (right) side of gauge
    * Displayed PV value (.VAL) text turns red when greater than this limit
 5. high - High alarm limit (.HIGH)
    * Presents as yellow bar on high (right) side of gauge
    * Displayed PV value (.VAL) text turns yellow when greater than this limit and less than hihi limit
 6. low - Low alarm limit (.LOW)
    * Presents as yellow bar on low (left) side of gauge
    * Displayed PV value (.VAL) text turns yellow when less than this limit and greater than lolo limit
 7. lolo - Low Low alarm limit (.LOLO)
    * Presents as red bar on low (left) side of gauge
    * Displayed PV value (.VAL) text turns red when less than this limit

## Dependencies
Built with Python 2.7 and requires the following packages:

* PyQt4 or greater
* PyEPICS
* PyDM
* numpy

Additionally requires EPICS Channel Access network IOC or PyDMSim to act as data server.

