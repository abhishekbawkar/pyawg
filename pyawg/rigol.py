from __future__ import annotations

import logging

from .base import AWG
from .enums import AmplitudeUnit, BurstModeRigol, BurstTriggerSource, FrequencyUnit, OutputLoad, WaveformType
from .exceptions import *


class RigolDG1000Z(AWG):
    """
    RigolDG1000Z is a class that represents the Rigol DG1000Z Arbitrary Waveform Generator (AWG). 
    It provides methods to control various parameters of the AWG such as amplitude, burst delay, 
    burst mode, burst period, burst state, burst trigger source, frequency, offset voltage, 
    output state, output load, phase, waveform type, phase synchronization, and burst triggering.

    Methods:
        __init__(self: RigolDG1000Z, ip_address):
        set_amplitude(self: RigolDG1000Z, channel: int, amplitude: float | int, unit: AmplitudeUnit = AmplitudeUnit.VPP) -> None:
        set_burst_delay(self: RigolDG1000Z, channel: int, delay: float | int) -> None:
        set_burst_mode(self: RigolDG1000Z, channel: int, burst_mode: BurstModeRigol) -> None:
        set_burst_period(self: RigolDG1000Z, channel: int, period: float | int) -> None:
        set_burst_state(self: RigolDG1000Z, channel: int, state: bool) -> None:
        set_burst_trigger_source(self: RigolDG1000Z, channel: int, trigger_source: BurstTriggerSource) -> None:
        set_frequency(self: RigolDG1000Z, channel: int, frequency: float | int, unit: FrequencyUnit = FrequencyUnit.HZ) -> None:
        set_offset(self: RigolDG1000Z, channel: int, offset_voltage: float | int) -> None:
        set_output(self: RigolDG1000Z, channel: int, state: bool) -> None:
        set_output_load(self: RigolDG1000Z, channel: int, load: OutputLoad | int | float) -> None:
        set_phase(self: RigolDG1000Z, channel: int, phase: float | int) -> None:
        set_waveform(self: RigolDG1000Z, channel: int, waveform_type: WaveformType) -> None:
        sync_phase(self: RigolDG1000Z, channel: int = 1) -> None:
        trigger_burst(self: RigolDG1000Z, channel: int) -> None:
            
    """

    def __init__(self: RigolDG1000Z, ip_address: str) -> None:
        """
        Initialize a RigolDG1000Z instance.

        Args:
            ip_address (str): The IP address of the Rigol DG1000Z device.

        """
        super().__init__(ip_address)
        logging.debug("RigolDG1000Z instance created.")

    def set_amplitude(self: RigolDG1000Z, channel: int, amplitude: float | int, unit: AmplitudeUnit = AmplitudeUnit.VPP) -> None:
        """
        Sets the amplitude for the specified channel on the RigolDG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            amplitude (float | int): The amplitude value to set (must be between -10 and 10).
            unit (AmplitudeUnit, optional): The unit of the amplitude (default is AmplitudeUnit.VPP).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the amplitude is not a float or int, or if the unit is not an instance of AmplitudeUnit.
            ValueError: If the amplitude is not between -10 and 10.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(amplitude) is not float and type(amplitude) is not int:
            raise TypeError(f"'amplitude' must be float or int; received {type(amplitude)}")
        elif not (-10 <= amplitude <= 10):
            raise ValueError(f"'amplitude' must be between -/+ 10")
        elif not isinstance(unit, AmplitudeUnit):
            raise TypeError(f"'unit' must be enum of type AmplitudeUnit. Hint: have you forgotten to import 'AmplitudeType' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:VOLT {amplitude}{unit.value}")
            logging.debug(f"Channel {channel} amplitude set to {amplitude}{unit.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} amplitude to {amplitude}{unit.value}: {e}")
            raise

    def set_burst_delay(self: RigolDG1000Z, channel: int, delay: float | int) -> None:
        """
        Sets the burst delay for the specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            delay (float | int): The delay time in seconds (must be non-negative).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the delay is not a float or int.
            ValueError: If the delay is negative.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(delay) is not float and type(delay) is not int:
            raise TypeError(f"'delay' must be float or int; received {type(delay)}")
        elif delay < 0:
            raise ValueError(f"'delay' cannot be negative")

        try:
            self.write(f"SOUR{channel}:BURS:TDEL {delay}")
            logging.debug(f"Channel {channel} burst delay has been set to {delay}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst delay to {delay}: {e}")

    def set_burst_mode(self: RigolDG1000Z, channel: int, burst_mode: BurstModeRigol) -> None:
        """
        Sets the burst mode for the specified channel on the Rigol DG1000Z.

        Args:
            channel (int): The channel number to set the burst mode for. Must be 1 or 2.
            burst_mode (BurstModeRigol): The burst mode to set. Must be an instance of BurstModeRigol.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If burst_mode is not an instance of BurstModeRigol.

        Logs:
            Debug: When the burst mode is successfully set.
            Error: If there is a failure in setting the burst mode.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(burst_mode, BurstModeRigol):
            raise TypeError(f"'burst_mode' must be enum of type BurstModeRigol. Hint: have you forgotten to import 'BurstModeRigol' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:BURS:MODE {burst_mode.value}")
            logging.debug(f"Channel {channel} burst mode has been set to {burst_mode.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst mode to {burst_mode.value}: {e}")

    def set_burst_period(self: RigolDG1000Z, channel: int, period: float | int) -> None:
        """
        Sets the burst period for the specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            period (float | int): The burst period to set. Must be a non-negative float or int.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the period is not a float or int.
            ValueError: If the period is negative.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(period) is not float and type(period) is not int:
            raise TypeError(f"'period' must be float or int; received {type(period)}")
        elif period < 0:
            raise ValueError(f"'period' cannot be negative")

        try:
            self.write(f"SOUR{channel}:BURS:INT:PER {period}")
            logging.debug(f"Channel {channel} burst period has been set to {period}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst period to {period}: {e}")

    def set_burst_state(self: RigolDG1000Z, channel: int, state: bool) -> None:
        """
        Set the burst state for a specified channel on the Rigol DG1000Z.

        Args:
            channel (int): The channel number to set the burst state for. Must be 1 or 2.
            state (bool): The desired burst state. True to turn burst on, False to turn it off.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the state is not a boolean.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")

        state_str = "ON" if state else "OFF"
        try:
            self.write(f"SOUR{channel}:BURS {state_str}")
            logging.debug(f"Channel {channel} burst state has been set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst state to {state_str}: {e}")

    def set_burst_trigger_source(self: RigolDG1000Z, channel: int, trigger_source: BurstTriggerSource) -> None:
        """
        Set the burst trigger source for a specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            trigger_source (BurstTriggerSource): The burst trigger source, which must be an instance of the BurstTriggerSource enum.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the trigger_source is not an instance of the BurstTriggerSource enum.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(trigger_source, BurstTriggerSource):
            raise TypeError(f"'trigger_source' must be enum of type BurstTriggerSource. Hint: have you forgotten to import 'BurstTriggerSource' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:BURS:TRIG:SOUR {trigger_source.value}")
            logging.debug(f"Channel {channel} burst trigger source has been set to {trigger_source.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst trigger source to {trigger_source.value}: {e}")

    def set_frequency(self: RigolDG1000Z, channel: int, frequency: float | int, unit: FrequencyUnit = FrequencyUnit.HZ) -> None:
        """
        Set the frequency for a specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            frequency (float | int): The frequency value to set (must be non-negative).
            unit (FrequencyUnit, optional): The unit of the frequency (default is FrequencyUnit.HZ).
        
        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the frequency is not a float or int, or if the unit is not an instance of FrequencyUnit.
            ValueError: If the frequency is negative.
            Exception: If there is an error in writing the frequency to the device.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(frequency) is not float and type(frequency) is not int:
            raise TypeError(f"'frequency' must be float or int; received {type(frequency)}")
        elif frequency < 0:
            raise ValueError(f"'frequency' cannot be negative")
        elif not isinstance(unit, FrequencyUnit):
            raise TypeError(f"'unit' must be enum of type FrequencyUnit. Hint: did you forget to import 'FrequencyUnit' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:FREQ {frequency}{unit.value}")
            logging.debug(f"Channel {channel} frequency set to {frequency}{unit.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} frequency to {frequency}{unit.value}: {e}")
            raise

    def set_offset(self: RigolDG1000Z, channel: int, offset_voltage: float | int) -> None:
        """
        Sets the offset voltage for the specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number to set the offset voltage for. Must be 1 or 2.
            offset_voltage (float | int): The offset voltage to set. Must be a float or int.
        
        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the offset_voltage is not a float or int.
            Exception: If there is an error in writing the offset voltage to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(offset_voltage) is not float and type(offset_voltage) is not int:
            raise TypeError(f"'offset_voltage' must be float or int; received {type(offset_voltage)}")

        try:
            self.write(f"SOUR{channel}:VOLT:OFFS {offset_voltage}")
            logging.debug(f"Channel {channel} offset voltage set to {offset_voltage} Vdc")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} offset voltage to {offset_voltage} Vdc: {e}")
            raise

    def set_output(self: RigolDG1000Z, channel: int, state: bool) -> None:
        """
        Sets the output state of the specified channel on the Rigol DG1000Z.

        Args:
            channel (int): The channel number to set the output state for. Must be 1 or 2.
            state (bool): The desired output state. True for ON, False for OFF.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the state is not a boolean.

        Returns:
            None
        
        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")


        state_str = "ON" if state else "OFF"
        try:
            self.write(f"OUTP{channel} {state_str}")
            logging.debug(f"Channel {channel} output has been set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output to {state_str}: {e}")

    def set_output_load(self: RigolDG1000Z, channel: int, load: OutputLoad | int | float) -> None:
        """
        Set the output load for a specified channel on the Rigol DG1000Z.
        
        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number to set the output load for. Must be 1 or 2.
            load (OutputLoad | int | float): The load value to set. Can be a float, int, or an instance of the OutputLoad enum.
        
        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the load is not a float, int, or an instance of OutputLoad.
        
        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(load) is not float and type(load) is not int and not isinstance(load, OutputLoad):
            raise TypeError(f"'load' must be float or int or enum of type OutputLoad; received {type(load)}. Hint: did you forget to import 'OutputLoad' from 'pyawg'?")

        if load == OutputLoad.HZ or load == OutputLoad.INF:
            load = 'INF'
        try:
            self.write(f"OUTP{channel}:LOAD {load}")
            logging.debug(f"Channel {channel} output load has been set to {load}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output load to {load}: {e}")

    def set_phase(self: RigolDG1000Z, channel: int, phase: float | int) -> None:
        """
        Set the phase of the specified channel on the Rigol DG1000Z.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number (must be 1 or 2).
            phase (float | int): The phase value to set, in degrees (must be between 0 and 360).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the phase is not a float or int.
            ValueError: If the phase is not between 0 and 360 degrees.
            Exception: If there is an error in writing the phase to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(phase) is not float and type(phase) is not int:
            raise TypeError(f"'phase' must be float or int; received {type(phase)}")
        elif not (0 <= abs(phase) <= 360):
            raise ValueError(f"'phase' must be between 0 and 360")

        try:
            self.write(f"SOUR{channel}:PHAS {phase}")
            logging.debug(f"Channel {channel} phase set to {phase}°")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} phase to {phase}°: {e}")
            raise

    def set_waveform(self: RigolDG1000Z, channel: int, waveform_type: WaveformType) -> None:
        """
        Sets the waveform type for the specified channel.

        Args:
            self (RigolDG1000Z): The instance of the RigolDG1000Z class.
            channel (int): The channel number to set the waveform for. Must be 1 or 2.
            waveform_type (WaveformType): The type of waveform to set. Must be an instance of the WaveformType enum.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the waveform_type is not an instance of WaveformType.
            Exception: If there is an error in writing the waveform type to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(waveform_type, WaveformType):
            raise TypeError(f"'waveform_type' must be enum of type WaveformType. Hint: have you forgotten to import 'WaveformType' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:FUNC {waveform_type.value}")
            logging.debug(f"Channel {channel} waveform set to {waveform_type.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} waveform to {waveform_type.value}: {e}")
            raise

    def sync_phase(self: RigolDG1000Z, channel: int = 1) -> None:
        """
        Synchronize the phase of the specified channel with the other channel.
        
        This method sends a command to the Rigol DG1000Z function generator to 
        synchronize the phase of the specified channel with the other channel.
        
        Args:
            channel (int): The channel number to synchronize (1 or 2). Defaults to 1.
        
        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)

        try:
            self.write(f"SOUR{channel}:PHAS:SYNC")
            logging.debug(f"Phases of both the channels have been synchronized")
        except Exception as e:
            logging.error(f"Failed to synchronize phase: {e}")
            raise

    def trigger_burst(self: RigolDG1000Z, channel: int) -> None:
        """
        Triggers a burst on the specified channel of the Rigol DG1000Z signal generator.

        Args:
            channel (int): The channel number to trigger the burst on. Must be 1 or 2.

        Raises:
            InvalidChannelNumber: If the provided channel number is not 1 or 2.
            Exception: If there is an error while sending the trigger command to the device.

        Returns:
            None

        """

        if type(channel) is not int or not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)

        try:
            self.write(f"SOUR{channel}:BURS:TRIG")
            logging.debug(f"Burst on channel {channel} has been successfully triggered")
        except Exception as e:
            logging.error(f"Failed to trigger the burst on channel {channel}: {e}")
