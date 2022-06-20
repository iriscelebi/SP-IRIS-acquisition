"Bindings for Thorlabs Benchtop Stepper Motor DLL"
# flake8: noqa
from ctypes import (
    Structure,
    cdll,
    c_bool,
    c_short,
    c_int,
    c_uint,
    c_int16,
    c_int32,
    c_char,
    c_byte,
    c_long,
    c_float,
    c_double,
    POINTER,
    CFUNCTYPE,
)

from thorlabs_kinesis._utils import (
    c_word,
    c_dword,
    bind
)

lib = cdll.LoadLibrary("Thorlabs.MotionControl.KCube.Piezo.dll")


# enum FT_Status
FT_OK = c_short(0x00)
FT_InvalidHandle = c_short(0x01)
FT_DeviceNotFound = c_short(0x02)
FT_DeviceNotOpened = c_short(0x03)
FT_IOError = c_short(0x04)
FT_InsufficientResources = c_short(0x05)
FT_InvalidParameter = c_short(0x06)
FT_DeviceNotPresent = c_short(0x07)
FT_IncorrectDevice = c_short(0x08)
FT_Status = c_short

# enum MOT_MotorTypes
MOT_NotMotor = c_int(0)
MOT_DCMotor = c_int(1)
MOT_StepperMotor = c_int(2)
MOT_BrushlessMotor = c_int(3)
MOT_CustomMotor = c_int(100)
MOT_MotorTypes = c_int

# enum KPZ_WheelDirectionSense
KPZ_WM_Positive = c_int16(0x01)
KPZ_WM_Negative = c_int16(0x02)
KPZ_WheelDirectionSense = c_int16

# enum KPZ_WheelMode
KPZ_WM_MoveAtVoltage = c_int16(0x01)
KPZ_WM_JogVoltage = c_int16(0x02)
KPZ_WM_SetVoltage = c_int16(0x03)
KPZ_WheelMode = c_int16

# enum KPZ_WheelChangeRate
KPZ_WM_High = c_int16(0x01)
KPZ_WM_Medium = c_int16(0x02)
KPZ_WM_Low = c_int16(0x03)
KPZ_WheelChangeRate = c_int16

# enum KPZ_TriggerPortMode
KPZ_TrigDisabled = c_int16(0x00)
KPZ_TrigIn_GPI = c_int16(0x01)
KPZ_TrigIn_VoltageStepUp = c_int16(0x02)
KPZ_TrigIn_VoltageStepDown = c_int16(0x03)
KPZ_TrigOut_GPO = c_int16(0x0A)
KPZ_TriggerPortMode = c_int16

# enum KPZ_TriggerPortPolarity
KPZ_TrigPolarityHigh = c_int16(0x01)
KPZ_TrigPolarityLow = c_int16(0x02)
KPZ_TriggerPortPolarity = c_int16

# enum PZ_ControlModeTypes
PZ_ControlModeUndefined = c_short(0)
PZ_OpenLoop = c_short(1)
PZ_CloseLoop = c_short(2)
PZ_OpenLoopSmooth = c_short(3)
PZ_CloseLoopSmooth = c_short(4)
PZ_ControlModeTypes = c_short

# enum PZ_InputSourceFlags
PZ_SoftwareOnly = c_short(0)
PZ_ExternalSignal = c_short(0x01)
PZ_Potentiometer = c_short(0x02)
PZ_All = PZ_ExternalSignal or PZ_Potentiometer 
PZ_InputSourceFlags = c_short

# enum PZ_OutputLUTModes
PZ_Continuous = c_short(0x01)
PZ_Fixed = c_short(0x02)
PZ_OutputTrigEnable = c_short(0x04)
PZ_InputTrigEnable = c_short(0x08)
PZ_OutputTrigSenseHigh = c_short(0x10)
PZ_InputTrigSenseHigh = c_short(0x20)
PZ_OutputGated = c_short(0x40)
PZ_OutputTrigRepeat = c_short(0x80)
PZ_OutputLUTModes = c_short

# enum HubAnalogueModes : short
AnalogueCh1 = c_short(1)
AnalogueCh2 = c_short(2)
ExtSignalSMA = c_short(3)
HubAnalogueModes = c_short

class TLI_DeviceInfo(Structure):
    _fields_ = [("typeID", c_dword),
                ("description", (65 * c_char)),
                ("serialNo", (9 * c_char)),
                ("PID", c_dword),
                ("isKnownType", c_bool),
                ("motorType", MOT_MotorTypes),
                ("isPiezoDevice", c_bool),
                ("isLaser", c_bool),
                ("isCustomType", c_bool),
                ("isRack", c_bool),
                ("maxChannels", c_short)]


class TLI_HardwareInformation(Structure):
    _fields_ = [("serialNumber", c_dword),
                ("modelNumber", (8 * c_char)),
                ("type", c_word),
                ("firmwareVersion", c_dword),
                ("notes", (48 * c_char)),
                ("deviceDependantData", (12 * c_byte)),
                ("hardwareVersion", c_word),
                ("modificationState", c_word),
                ("numChannels", c_short)]


class PZ_FeedbackLoopConstants(Structure):
    _fields_ = [("proportionalTerm", c_short),
                ("integralTerm", c_short)]

				
				
class PZ_LUTWaveParameters(Structure):
    _fields_ = [("mode", PZ_OutputLUTModes),
                ("cycleLength", c_short),
                ("numCycles", c_uint),
                ("LUTValueDelay", c_uint),
                ("preCycleDelay", c_uint),
                ("postCycleDelay", c_uint),
                ("outTriggerStart", c_short),
                ("outTriggerDuration", c_uint),
                ("numOutTriggerRepeat", c_short)]		

class KPZ_MMIParams(Structure):
    _fields_ = [("VoltageAdjustRate", KPZ_WheelChangeRate),
                ("VoltageStep", c_int32),
                ("JoystickDirectionSense", KPZ_WheelDirectionSense),
                ("PresetPos1", c_int32),
                ("PresetPos2", c_int32),
                ("DisplayIntensity", c_int16),
                ("DisplayTimeout", c_int16),
                ("DisplayDimIntensity", c_int16),
                ("reserved", (4 * c_int16))]					
				
class KPZ_TriggerConfig(Structure):
    _fields_ = [("Trigger1Mode", KPZ_TriggerPortMode),
                ("Trigger1Polarity", KPZ_TriggerPortPolarity),
                ("Trigger2Mode", KPZ_TriggerPortMode),
                ("Trigger2Polarity", KPZ_TriggerPortPolarity),
                ("reserved", (6 * c_int16))]		


				
##################################################################


TLI_BuildDeviceList = bind(lib, "TLI_BuildDeviceList", None, c_short)
TLI_GetDeviceListSize = bind(lib, "TLI_GetDeviceListSize", None, c_short)
# TLI_GetDeviceList  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceList(SAFEARRAY** stringsReceiver);
# TLI_GetDeviceListByType  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByType(SAFEARRAY** stringsReceiver, int typeID);
# TLI_GetDeviceListByTypes  <- TODO: Implement SAFEARRAY first. BENCHTOPSTEPPERMOTOR_API short __cdecl TLI_GetDeviceListByTypes(SAFEARRAY** stringsReceiver, int * typeIDs, int length);
TLI_GetDeviceListExt = bind(lib, "TLI_GetDeviceListExt", [POINTER(c_char), c_dword], c_short)
TLI_GetDeviceListByTypeExt = bind(lib, "TLI_GetDeviceListByTypeExt", [POINTER(c_char), c_dword, c_int], c_short)
TLI_GetDeviceListByTypesExt = bind(lib, "TLI_GetDeviceListByTypesExt", [POINTER(c_char), c_dword, POINTER(c_int), c_int], c_short)
TLI_GetDeviceInfo = bind(lib, "TLI_GetDeviceInfo", [POINTER(c_char), POINTER(TLI_DeviceInfo)], c_short)

PCC_Open = bind(lib, "PCC_Open", [POINTER(c_char)], c_short)
PCC_Close = bind(lib, "PCC_Close", [POINTER(c_char)])
PCC_SetZero = bind(lib, "PCC_SetZero", [POINTER(c_char)], c_bool)
PCC_SetOutputVoltage = bind(lib, "PCC_SetOutputVoltage", [POINTER(c_char), c_short], c_short)
PCC_GetPosition = bind(lib, "PCC_GetPosition", [POINTER(c_char)], c_word)
PCC_GetOutputVoltage = bind(lib, "PCC_GetOutputVoltage", [POINTER(c_char)], c_short)

"""
SBC_CheckConnection = bind(lib, "SBC_CheckConnection", [POINTER(c_char)], c_bool)
SBC_IsChannelValid = bind(lib, "SBC_IsChannelValid", [POINTER(c_char), c_short], c_bool)
"""

"""
SBC_GetHardwareInfo = bind(lib, "SBC_GetHardwareInfo", [POINTER(c_char), c_short, POINTER(c_char), c_dword, POINTER(c_word), POINTER(c_word), POINTER(c_char), c_dword, POINTER(c_dword), POINTER(c_word), POINTER(c_word)], c_short)
SBC_GetHardwareInfoBlock = bind(lib, "SBC_GetHardwareInfoBlock", [POINTER(c_char), c_short, POINTER(TLI_HardwareInformation)], c_short)
SBC_GetNumChannels = bind(lib, "SBC_GetNumChannels", [POINTER(c_char)], c_short)
SBC_GetFirmwareVersion = bind(lib, "SBC_GetFirmwareVersion", [POINTER(c_char), c_short], c_dword)
SBC_GetSoftwareVersion = bind(lib, "SBC_GetSoftwareVersion", [POINTER(c_char)])
SBC_LoadSettings = bind(lib, "SBC_LoadSettings", [POINTER(c_char), c_short], c_bool)
SBC_PersistSettings = bind(lib, "SBC_PersistSettings", [POINTER(c_char), c_short], c_bool)
SBC_SetCalibrationFile = bind(lib, "SBC_SetCalibrationFile", [POINTER(c_char), c_short, POINTER(c_char), c_bool])
SBC_IsCalibrationActive = bind(lib, "SBC_IsCalibrationActive", [POINTER(c_char), c_short], c_bool)
SBC_GetCalibrationFile = bind(lib, "SBC_GetCalibrationFile", [POINTER(c_char), c_short, POINTER(c_char), c_short], c_bool)
SBC_DisableChannel = bind(lib, "SBC_DisableChannel", [POINTER(c_char), c_short], c_short)
SBC_EnableChannel = bind(lib, "SBC_EnableChannel", [POINTER(c_char), c_short], c_short)
"""

PCC_StartPolling = bind(lib, "PCC_StartPolling", [POINTER(c_char), c_int], c_bool)
PCC_ClearMessageQueue = bind(lib, "PCC_ClearMessageQueue", [POINTER(c_char)])
PCC_StopPolling = bind(lib, "PCC_StopPolling", [POINTER(c_char)])
