import serial
import matplotlib.pyplot as plot

def who():
    '''
        Sends an identification query to the SCPI device and parses the response
        to get the brand, model, calibration factor, firmware version, 
        and the device's communication module.
    '''
    formattedOut = {}

    ser = serial.Serial('COM3', 9600, timeout=1)
    ser.write(b'*IDN?\n')
    response = ser.readline().decode().strip()
    ser.close()

    specifics = response.split(',')

    formattedOut['Brand'] = specifics[0]
    formattedOut['Model'] = specifics[1]
    
    remaining =  specifics[3].split(' ')

    formattedOut['Calibration_Factor'] = remaining[0].split(':')[1]
    formattedOut['Firmware_Version'] = remaining[1].split(':')[1]
    formattedOut['Comm_Module'] = remaining[2]

    return formattedOut


def WaveSpecs():
    '''
        Sends a query to get waveform preamble details from the SCPI device.
        Parses the response to extract waveform specifications such as:
        bits per sample, encoding, points, sample interval, and voltage scale.
    '''
    print('Loading waveform details...')
    ser = serial.Serial('COM3', 9600, timeout=1)

    ser.write(b'WFMPRE?\n')
    WavePreamble = ser.readline().decode().strip()
    print('Waveform details loaded.')

    WaveConditions = WavePreamble.split(';')

    WaveSpecification = {}
    WaveSpecification['Bits/Sample'] = WaveConditions[1]
    WaveSpecification['Encoding'] = WaveConditions[2]
    WaveSpecification['Points'] = WaveConditions[5]
    WaveSpecification['Summary'] = WaveConditions[6]
    WaveSpecification['SampleInterval'] = WaveConditions[8]
    WaveSpecification['Bits/Sample'] = WaveConditions[10]
    WaveSpecification['VoltageScale'] = WaveConditions[12]

    ser.close()
    
    return WaveSpecification


def ch1Voltage():
    '''
        Sends a query to get voltage levels from the SCPI device.
        Parses the response to get the voltage data.
    '''
    print('Loading voltage levels...')

    ser = serial.Serial('COM3', 9600, timeout=1)

    ser.write(b'CURVE?\n')
    rawVolts = ser.readline().decode().strip()

    print('Voltage Levels Loaded.')

    voltage = rawVolts.split(',')

    ser.close()
    return voltage


def VT_Data():
    '''
        Utilizes WaveSpecs() and ch1Voltage() to gather and scale voltage data over time, 
        storing the data in a dictionary where keys are times and values are voltages.
    '''
    Volt_vs_Time = {}
    time = 0
    print('===========================')
    print('=Starting Data Acquisition=')
    print('===========================')
    WaveInfo = WaveSpecs()
    time_interval = float(WaveInfo.get('SampleInterval'))
    voltage_scale = float(WaveInfo.get('VoltageScale'))
    voltage_data = ch1Voltage()
    for sample in voltage_data:
        Volt_vs_Time[time] = float(sample) * voltage_scale
        time += time_interval


    return Volt_vs_Time

def graph(xyData):
    '''
        Plots voltage vs.time data using matplotlib. 
        If no data is provided, it calls VT_Data() to generate the data to be plotted.
    '''
    if xyData == None:
        xyData = VT_Data()

    x_data = []
    y_data = []

    for key in xyData.keys():
        x_data.append(key)
        y_data.append(xyData.get(key))

    plot.plot(x_data, y_data)
    plot.title('Voltage vs Time')
    plot.xlabel('Time (s)')
    plot.ylabel('Voltage (V)')
    plot.grid(linestyle=':', linewidth=2)
    plot.show()

    return 1

def baseAnalysis(data):
    '''
        Performs basic analysis on voltage data to calculate the range, average, maximum, and minimum voltages.
    '''
    if type(data) != dict:
        print('Input must be dictionary.')
        return 0
    max = data[0]
    min = data[0]
    for voltage in data.values():
        if voltage > max:
            max = float(voltage)
        elif voltage < min:
            min = float(voltage)

    Vrange = max - min
    Vavg = (max + min) / 2

    Basic_Values = {'VRange':Vrange,'VAvg':Vavg,'VMax':max,'VMin':min}

    return Basic_Values


if __name__ == '__main__':
    Data = VT_Data()
    
    BasicAnalysis = baseAnalysis(Data)
    print(BasicAnalysis)
    graph(Data)
