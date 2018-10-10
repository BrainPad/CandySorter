alarms = {
    "0x00": {
        "Category": "Public Alarm",
        "Name": "Reset Alarm",
        "SetCondition": " After the system reset, the reset alarm will be set automatically",
        "ResetCondition": " Protocol instruction is cleared"
    },
    "0x01": {
        "Category": "Public Alarm",
        "Name": "Undefined Instruction",
        "SetCondition": "Undifined instruction is received",
        "ResetCondition": "The protocol instruction is cleared."
    },
    "0x02": {
        "Category": "Public Alarm",
        "Name": "File System Error",
        "SetCondition": "The file system errors;",
        "ResetCondition": "Reset, if the file system initialization is successful, then reset the alarm automatically."
    },
    "0x03": {
        "Category": "Public Alarm",
        "Name": "Failed Communication between MCU and FPGA",
        "SetCondition": "The communication between MCU and FPGA is failed when initialization;",
        "ResetCondition": "Reset, if the communication is successful, then reset the alarm automatically"
    },
    "0x04": {
        "Category": "Public Alarm",
        "Name": "Angle Sensor Reading Error",
        "SetCondition": "The angle sensor value can not be read correctly",
        "ResetCondition": "Power off, power on again, if the angle sensor value can be read correctly, then reset alarm."
    },
    "0x11": {
        "Category": "Planning Alarm",
        "Name": "Inverse Resolve Alarm",
        "SetCondition": "The planning target point is not in the robot work space, resulting in the reverse solution error",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x12": {
        "Category": "Planning Alarm",
        "Name": "Inverse Resolve Limit",
        "SetCondition": "Inverse resolve of the target point beyond the joint limit value",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x13": {
        "Category": "Planning Alarm",
        "Name": "Arc Input Parameter Alarm",
        "SetCondition": "Enter the midpoint of the arc, and the target point can not form an arc",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x15": {
        "Category": "Planning Alarm",
        "Name": "JUMP Parameter Error",
        "SetCondition": "The planning starting point or the target point height above the set maximum JUMP height",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x21": {
        "Category": "Kinematic Alarm",
        "Name": "Inverse Resolve Alarm",
        "SetCondition": "The movement process beyond the robot work space resulting in the inverse solution error",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x22": {
        "Category": "Kinematic Alarm",
        "Name": "Inverse Resolve Limit",
        "SetCondition": "The inverse solution of the motion exceeds the Joint limit value",
        "ResetCondition": "The protocol instruction is cleared"
    },
    "0x44": {
        "Category": "Limit Alarm",
        "Name": "Joint 3 Positive Limit Alarm",
        "SetCondition": "Joint 3 moves in the positive direction to the limit area",
        "ResetCondition": "Protocol command reset the alarm manually; reset the alarm in reverse exit limit area automatically"
    }
}