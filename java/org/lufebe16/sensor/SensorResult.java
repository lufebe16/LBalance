package org.lufebe16.sensor;

public class SensorResult
{
    // orientation angles.
    public double rawPhi = 0.0;
    public double rawTheta = 0.0;

    // balance relevant angles
    public double smPitch = 0.0;
    public double smRoll = 0.0;
    public double smBalanceX = 0.0;
    public double smBalanceY = 0.0;

    public SensorResult() {}
    public SensorResult(SensorResult vals)
    {
        smPitch = vals.smPitch;
        smRoll = vals.smRoll;
        smBalanceX = vals.smBalanceX;
        smBalanceY = vals.smBalanceY;
        rawPhi = vals.rawPhi;
        rawTheta = vals.rawTheta;
    }
}
