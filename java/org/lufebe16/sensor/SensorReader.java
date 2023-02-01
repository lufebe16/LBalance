package org.lufebe16.sensor;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;

import org.lufebe16.util.Smoother;
import org.lufebe16.sensor.SensorResult;

import android.util.Log;
/*
 *  Copyright (C) 2023 Lukas Beck
 *
 *  This is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  It is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with it. If not, see <http://www.gnu.org/licenses/>
 */
public class SensorReader implements SensorEventListener
{
    /**
     * Orientation
     */
    private SensorManager sensorManager;
    /**
      * Smoothing
     */
    private long halfLife = 300; // [ms]
    private Smoother angleSmooth;
    /**
     * indicates whether or not Accelerometer Sensor is supported
     */
    private Boolean supported = false;
    /**
     * indicates whether or not Accelerometer Sensor is running
     */
    private boolean running = false;
    //private boolean locked;

    public SensorReader() {
    }

    /*
     * Single Instance.
     */
    private static SensorReader provider;
    public static SensorReader getInstance()
    {
        if (provider == null) {
            provider = new SensorReader();
        }
        return provider;
    }

    /**
     * Returns true if at least one Accelerometer sensor is available
     */
    public boolean isSupported(Context context) {
        if (supported == false) {
            if (context != null) {
                sensorManager = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
                Sensor sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
                supported = (sensor != null);
            }
        }
        return supported;
    }

    /**
     * Returns true if the manager is listening to orientation changes
     */
    public boolean isListening() {
        return running;
    }

    /**
     * Unregisters listeners
     */
    public void stopListening() {
        running = false;
        try {
            if (sensorManager != null) {
                sensorManager.unregisterListener(this);
            }
        } catch (Exception e) {
        }
    }

    /**
     * Registers a listener and start listening
     * callback for accelerometer events
     */
    //public void startListening(OrientationListener orientationListener)
    public void startListening(Context context)
    {
        // smoother
        //halfLife = 150; // [ms]
        halfLife = 20; // [ms]
        angleSmooth = new Smoother(halfLife,-180.0,180.0);

        // register listener and start listening
        sensorManager = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        running = true;
        Sensor sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (sensor != null)
        {
            running = sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL) && running;
        }
    }

    public void onAccuracyChanged(Sensor sensor, int accuracy) {
    }

    private SensorResult valsSM = new SensorResult();

    private long lastTime = 0;
    private long deltaTime = 0;
    private long lastMilis = 0;

    private double[] evalues = new double[3];
    private Smoother esmooth = new Smoother(150);

    public void onSensorChanged(SensorEvent event)
    {
        long currentTime = event.timestamp / 1000000; // [ms]

        /*
         * folgendes nicht mehr notwendig (auser logs)
         */
        if (lastTime == 0) lastTime = currentTime;
        else {
            deltaTime = currentTime - lastTime;
            if (deltaTime <= 0) return;
            lastTime = currentTime;
        }
        Log.i("LevelProvider",String.format("onSensorChanged delta = %d",deltaTime));

        long curMilis = System.currentTimeMillis();
        if (lastMilis > 0) {
            Log.i("LevelProvider",String.format("onSensorChanged milis = %d",curMilis-lastMilis));
        }
        lastMilis = curMilis;

        /*
         * Eingangs Rauschfilter
         */
        esmooth.updateTime(currentTime);
        for (int i=0; i<3; i++) {
            evalues[i] = esmooth.updateValue(evalues[i],event.values[i]);
        }

        /*
         * signal aufbereiten.
         * Wir ermitteln diverse Winkel zum Schwerkraft Vektor.
         */

        // Drehung um die z-Achse (-180 to 180, darum atan2):
        // (Oft mit 'Psy' oder 'Phi' bezeichenter Winkel)
        double xyAngle = Math.toDegrees(Math.atan2(evalues[1],evalues[0]));

        // Winkel zwischen z-Achse und xy-Ebene (-90..90)
        // (Oft mit 'theta' bezeichneter Winkel)
        double zxyAngle = Math.toDegrees(Math.atan(
                evalues[2]/Math.sqrt(evalues[0]*evalues[0]+evalues[1]*evalues[1])
                ));

        // Das wär eigentlich alles was wir zur Richtung der Schwerkraft bezüglich
        // unseres Apparates benötigen. Zusätzlich, der Einfachheit halber ermittlen
        // wir direkt noch die folgenden Werte direkt:

        // Drehung um die y-Achse ('roll', -90..90)
        double xzAngle = Math.toDegrees(Math.atan(evalues[0]/Math.abs(evalues[2])));

        // Drehung um die x-Achse ('pitch', -90..90)
        double yzAngle = -Math.toDegrees(Math.atan(evalues[1]/Math.abs(evalues[2])));

        // Wert für balanceX
        double yxAngle = 90.0-xyAngle;
        if (yxAngle>=180) yxAngle -= 360.0;

        /*
         * Smoothing.
         */
        angleSmooth.updateTime(currentTime);
        valsSM.smPitch = angleSmooth.updateValue(valsSM.smPitch,yzAngle);
        valsSM.smRoll = angleSmooth.updateValue(valsSM.smRoll,xzAngle);
        valsSM.smBalanceX = angleSmooth.updateValue(valsSM.smBalanceX,yxAngle);
        valsSM.smBalanceY = angleSmooth.updateValue(valsSM.smBalanceY,xyAngle);
        valsSM.rawPhi = xyAngle;
        valsSM.rawTheta = zxyAngle;
        //valsSM.rawPhi = angleSmooth.updateValue(valsSM.rawPhi,xyAngle);
        //valsSM.rawTheta = angleSmooth.updateValue(valsSM.rawTheta,zxyAngle);
    }

    public SensorResult getCurrentValues()
    {
        return new SensorResult(valsSM); 
    }
}
