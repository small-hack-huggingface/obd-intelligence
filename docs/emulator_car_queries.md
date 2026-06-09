# Emulator `car` scenario -- all 86 supported queries

Captured from `python obd_connection.py --discover` against `elm327-emulator -s car -n 35000`.

| Command | Sample value | Description |
|---------|--------------|-------------|
| ABSOLUTE_LOAD | 32.94 percent | Absolute load value |
| BAROMETRIC_PRESSURE | 97 kPa | Barometric Pressure |
| CATALYST_TEMP_B1S1 | 513.0 degC | Catalyst Temperature: Bank 1 - Sensor 1 |
| CATALYST_TEMP_B1S2 | 29.7 degC | Catalyst Temperature: Bank 1 - Sensor 2 |
| CLEAR_DTC | NULL | Clear DTCs and Freeze data |
| COMMANDED_EGR | 0.0 percent | Commanded EGR |
| COMMANDED_EQUIV_RATIO | 0.987 ratio | Commanded equivalence ratio |
| CONTROL_MODULE_VOLTAGE | 14.667 V | Control module voltage |
| COOLANT_TEMP | 55 degC | Engine Coolant Temperature |
| DISTANCE_SINCE_DTC_CLEAR | 50.0 km | Distance traveled since codes cleared |
| DISTANCE_W_MIL | 0.0 km | Distance Traveled with MIL on |
| DTC_ABSOLUTE_LOAD | 1807.1 percent | DTC Absolute load value |
| DTC_BAROMETRIC_PRESSURE | 18 kPa | DTC Barometric Pressure |
| DTC_CATALYST_TEMP_B1S1 | 420.8 degC | DTC Catalyst Temperature: Bank 1 - Sensor 1 |
| DTC_CATALYST_TEMP_B1S2 | 420.8 degC | DTC Catalyst Temperature: Bank 1 - Sensor 2 |
| DTC_COMMANDED_EGR | 7.06 percent | DTC Commanded EGR |
| DTC_COMMANDED_EQUIV_RATIO | 0.141 ratio | DTC Commanded equivalence ratio |
| DTC_CONTROL_MODULE_VOLTAGE | 4.608 V | DTC Control module voltage |
| DTC_COOLANT_TEMP | -22 degC | DTC Engine Coolant Temperature |
| DTC_DISTANCE_SINCE_DTC_CLEAR | 4608.0 km | DTC Distance traveled since codes cleared |
| DTC_DISTANCE_W_MIL | 4608.0 km | DTC Distance Traveled with MIL on |
| DTC_ENGINE_LOAD | 7.06 percent | DTC Calculated Engine Load |
| DTC_EVAPORATIVE_PURGE | 7.06 percent | DTC Commanded Evaporative Purge |
| DTC_FUEL_STATUS | NULL | DTC Fuel System Status |
| DTC_FUEL_TYPE | NULL | DTC Fuel Type |
| DTC_HYBRID_BATTERY_REMAINING | NULL | DTC Hybrid battery pack remaining life |
| DTC_INTAKE_PRESSURE | 18 kPa | DTC Intake Manifold Pressure |
| DTC_INTAKE_TEMP | -22 degC | DTC Intake Air Temp |
| DTC_LONG_FUEL_TRIM_1 | -85.9 percent | DTC Long Term Fuel Trim - Bank 1 |
| DTC_MAF | 46.08 g/s | DTC Air Flow Rate (MAF) |
| DTC_O2_B1S2 | 0.09 V | DTC O2: Bank 1 - Sensor 2 Voltage |
| DTC_O2_S1_WR_CURRENT | -128.0 mA | DTC O2 Sensor 1 WR Lambda Current |
| DTC_O2_S1_WR_VOLTAGE | 0.0 V | DTC O2 Sensor 1 WR Lambda Voltage |
| DTC_O2_SENSORS | (sensor bitmask) | DTC O2 Sensors Present |
| DTC_OBD_COMPLIANCE | EMD+ | DTC OBD Standards Compliance |
| DTC_PIDS_B | NULL | DTC Supported PIDs [21-40] |
| DTC_PIDS_C | NULL | DTC Supported PIDs [41-60] |
| DTC_RELATIVE_THROTTLE_POS | 7.06 percent | DTC Relative throttle position |
| DTC_RPM | 1152 rpm | DTC Engine RPM |
| DTC_RUN_TIME | 4608 s | DTC Engine Run Time |
| DTC_RUN_TIME_MIL | 4608 min | DTC Time run with MIL on |
| DTC_SHORT_FUEL_TRIM_1 | -85.9 percent | DTC Short Term Fuel Trim - Bank 1 |
| DTC_SPEED | 18.0 km/h | DTC Vehicle Speed |
| DTC_STATUS | Status object | DTC Status since DTCs cleared |
| DTC_THROTTLE_ACTUATOR | 7.06 percent | DTC Commanded throttle actuator |
| DTC_THROTTLE_POS | 7.06 percent | DTC Throttle Position |
| DTC_THROTTLE_POS_B | 7.06 percent | DTC Absolute throttle position B |
| DTC_TIME_SINCE_DTC_CLEARED | 4608 min | DTC Time since trouble codes cleared |
| DTC_TIMING_ADVANCE | -55.0 deg | DTC Timing Advance |
| DTC_WARMUPS_SINCE_DTC_CLEAR | NULL | DTC Number of warm-ups since codes cleared |
| ELM_VERSION | ELM327 v1.5 | ELM327 version string |
| ELM_VOLTAGE | 13.1 V | Voltage detected by OBD-II adapter |
| ENGINE_LOAD | 100.0 percent | Calculated Engine Load |
| EVAPORATIVE_PURGE | 0.0 percent | Commanded Evaporative Purge |
| FUEL_STATUS | NULL | Fuel System Status |
| FUEL_TYPE | Gasoline | Fuel Type |
| GET_CURRENT_DTC | [] | Get DTCs from the current/last driving cycle |
| GET_DTC | [] | Get DTCs |
| HYBRID_BATTERY_REMAINING | NULL | Hybrid battery pack remaining life |
| INTAKE_PRESSURE | 38 kPa | Intake Manifold Pressure |
| INTAKE_TEMP | 17 degC | Intake Air Temp |
| LONG_FUEL_TRIM_1 | -5.5 percent | Long Term Fuel Trim - Bank 1 |
| MAF | 61.75 g/s | Air Flow Rate (MAF) |
| MIDS_A | bitmask | Supported MIDs [01-20] |
| O2_B1S2 | 0.035 V | O2: Bank 1 - Sensor 2 Voltage |
| O2_S1_WR_CURRENT | -0.059 mA | O2 Sensor 1 WR Lambda Current |
| O2_S1_WR_VOLTAGE | 3.18 V | O2 Sensor 1 WR Lambda Voltage |
| O2_SENSORS | (sensor bitmask) | O2 Sensors Present |
| OBD_COMPLIANCE | EOBD (Europe) | OBD Standards Compliance |
| PIDS_9A | bitmask | Supported PIDs [01-20] |
| PIDS_A | bitmask | Supported PIDs [01-20] |
| PIDS_B | bitmask | Supported PIDs [21-40] |
| PIDS_C | bitmask | Supported PIDs [41-60] |
| RELATIVE_THROTTLE_POS | 9.8 percent | Relative throttle position |
| RPM | 1303.75 rpm | Engine RPM |
| RUN_TIME | 117 s | Engine Run Time |
| RUN_TIME_MIL | 0 min | Time run with MIL on |
| SHORT_FUEL_TRIM_1 | 0.0 percent | Short Term Fuel Trim - Bank 1 |
| SPEED | 10 km/h | Vehicle Speed |
| STATUS | Status object | Status since DTCs cleared |
| THROTTLE_ACTUATOR | 44.3 percent | Commanded throttle actuator |
| THROTTLE_POS | 16.9 percent | Throttle Position |
| THROTTLE_POS_B | 57.3 percent | Absolute throttle position B |
| TIME_SINCE_DTC_CLEARED | 91 min | Time since trouble codes cleared |
| TIMING_ADVANCE | -5.5 deg | Timing Advance |
| WARMUPS_SINCE_DTC_CLEAR | 4 | Number of warm-ups since codes cleared |
