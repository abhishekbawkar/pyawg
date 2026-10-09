# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 Abhishek Bawkar
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from typing import Optional, Union

from .base import AWG
from .enums import (
    AmplitudeUnit,
    BurstModeSiglent,
    BurstTriggerSource,
    FrequencyUnit,
    OutputLoad,
    PulseWidthUnit,
    WaveformType,
)
from .exceptions import UnsupportedModel


class SiglentSDG1000X(AWG):
    """
    SiglentSDG1000X is a class that represents the Siglent SDG1000X / SDG1000X Plus Arbitrary Waveform
    Generator (AWG). It provides methods to control various parameters of the AWG such as amplitude,
    burst delay, burst mode, burst period, burst state, burst trigger source, frequency, offset voltage,
    output state, output load, phase, waveform type, phase synchronization, and burst triggering.

    Burst parameters (mode, cycles, trigger source, period, delay) can only be set while burst is ON:
    call `set_burst_state(channel, True)` first. Enabling burst resets them to the instrument defaults.

    Methods:
        __init__(self: SiglentSDG1000X, ip_address):
        get_burst_parameter(self: SiglentSDG1000X, channel: int, parameter: str) -> str:
        get_channel_wave_parameter(self: SiglentSDG1000X, channel: int, parameter: str) -> str:
        set_amplitude(self: SiglentSDG1000X, channel: int, amplitude: Union[float, int], unit: AmplitudeUnit = AmplitudeUnit.VPP) -> None:
        set_burst_cycles(self: SiglentSDG1000X, channel: int, cycles: Union[int, str]) -> None:
        set_burst_delay(self: SiglentSDG1000X, channel: int, delay: Union[float, int]) -> None:
        set_burst_mode(self: SiglentSDG1000X, channel: int, burst_mode: BurstModeSiglent) -> None:
        set_burst_period(self: SiglentSDG1000X, channel: int, period: Union[float, int]) -> None:
        set_burst_run_state(self: SiglentSDG1000X, channel: int, run: bool) -> None:
        set_burst_state(self: SiglentSDG1000X, channel: int, state: bool) -> None:
        set_burst_trigger_source(self: SiglentSDG1000X, channel: int, trigger_source: BurstTriggerSource) -> None:
        set_duty_cycle(self: SiglentSDG1000X, channel: int, duty_cycle: Union[float, int]) -> None:
        set_frequency(self: SiglentSDG1000X, channel: int, frequency: Union[float, int], unit: FrequencyUnit = FrequencyUnit.HZ) -> None:
        set_offset(self: SiglentSDG1000X, channel: int, offset_voltage: Union[float, int]) -> None:
        set_output(self: SiglentSDG1000X, channel: int, state: bool) -> None:
        set_output_load(self: SiglentSDG1000X, channel: int, load: Union[float, int, OutputLoad]) -> None:
        set_phase(self: SiglentSDG1000X, channel: int, phase: Union[float, int]) -> None:
        set_pulse_width(self: SiglentSDG1000X, channel: int, pulse_width: Union[float, int], unit: PulseWidthUnit = PulseWidthUnit.S) -> None:
        set_waveform(self: SiglentSDG1000X, channel: int, waveform_type: WaveformType) -> None:
        sync_phase(self: SiglentSDG1000X, channel: int = 1) -> None:
        trigger_burst(self: SiglentSDG1000X, channel: int) -> None:

    """

    def __init__(self, ip_address):
        """
        Initialize a SiglentSDG1000X instance.

        Args:
            ip_address (str): The IP address of the Siglent SDG1000X device.

        """
        super().__init__(ip_address)
        logging.debug("SiglentSDG1000X instance created.")

        self.MAX_CHANNELS = 2
        self.MAX_FREQUENCY = 3e7 if "1032" in self.model else 6e7
        self.MIN_FREQUENCY = 0
        # Vpp into High-Z; into 50 Ohm the instrument allows half of it.
        self.MAX_AMPLITUDE = 20.0
        self.MIN_AMPLITUDE = 0.001
        self.MAX_BURST_CYCLES = 1_000_000

    @staticmethod
    def _parse_reply(reply: str) -> dict:
        """
        Parses a `C<n>:XXXX key,value,...` reply into a dict.

        Bare section markers (e.g. CARR in a BTWV? reply) carry no value. Parsing stops at CARR, so a
        burst reply yields only the burst's own fields; carrier fields are read with BSWV?.
        """
        parts = reply.strip().strip("'").split(" ", 1)[-1].split(",")
        params = {}
        index = 0
        while index < len(parts) - 1:
            if parts[index] == "CARR":
                break
            params[parts[index]] = parts[index + 1]
            index += 2
        return params

    def _require_burst_on(self: SiglentSDG1000X, channel: int) -> None:
        """
        Raises if burst is OFF on the channel. The instrument ignores burst parameters until burst
        is ON, and enabling it afterwards resets them to defaults.
        """
        state = self._parse_reply(self.query(f"C{channel}:BTWV?")).get("STATE")
        if state != "ON":
            raise RuntimeError(
                f"Burst is OFF on channel {channel}; call set_burst_state({channel}, True) before setting burst parameters"
            )

    def _validate_amplitude(self: SiglentSDG1000X, amplitude: Union[float, int]) -> None:
        """
        Validates the amplitude (Vpp) for the Siglent SDG1000X.

        Raises:
            TypeError: If the amplitude is not a float or int.
            ValueError: If the amplitude is not between MIN_AMPLITUDE and MAX_AMPLITUDE.
        """
        if (type(amplitude) is not int) and (type(amplitude) is not float):
            raise TypeError(
                f"'amplitude' must be float or int; received {type(amplitude)}"
            )
        if not self.MIN_AMPLITUDE <= amplitude <= self.MAX_AMPLITUDE:
            raise ValueError(
                f"'amplitude' must be between {self.MIN_AMPLITUDE} and {self.MAX_AMPLITUDE} Vpp"
            )

    def get_burst_parameter(self: SiglentSDG1000X, channel: int, parameter: str) -> Optional[str]:
        """
        Gets a burst parameter for the specified channel.

        Args:
            channel (int): The channel number to query.
            parameter (str): Valid options are 'state', 'period', 'trigger_source', 'trigger_mode',
                'cycles', 'delay', 'mode' and 'counter'. A field the instrument does not report in its
                current configuration returns None.

        Returns:
            Optional[str]: The value of the requested parameter.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            KeyError: If the parameter is not one of the valid options.
            Exception: If there is an error in querying the burst parameters.

        """
        self._validate_channel(channel)
        try:
            params = self._parse_reply(self.query(f"C{channel}:BTWV?"))
            result_dict = {
                "state": params.get("STATE"),
                "period": params.get("PRD"),
                "trigger_source": params.get("TRSR"),
                "trigger_mode": params.get("TRMD"),
                "cycles": params.get("TIME"),
                "delay": params.get("DLAY"),
                "mode": params.get("GATE_NCYC"),
                "counter": params.get("COUNTER"),
            }
            return result_dict[parameter]

        except Exception as e:
            logging.error(f"Failed to retrieve burst parameter and/or its value: {e}")
            raise

    def get_channel_wave_parameter(
        self: SiglentSDG1000X, channel: int, parameter: str
    ) -> Optional[str]:
        """
        Gets the waveform parameters for the specified channel.

        Args:
            channel (int): The channel number to query.
            parameter (str): The specific parameter to retrieve. Valid options are 'waveform_type',
                'frequency', 'period', 'amplitude', 'offset', 'high_level', 'low_level', 'phase',
                'duty_cycle', 'pulse_width', 'rise', 'fall' and 'delay'. A field the current waveform
                does not have returns None.

        Returns:
            Optional[str]: The value of the requested parameter.

        Raises:
            Exception: If there is an error in querying the waveform parameters or retrieving the value.

        """

        try:
            params = self._parse_reply(self.query(f"C{channel}:BSWV?"))

            result_dict = {
                "waveform_type": params.get("WVTP"),
                "frequency": params.get("FRQ"),
                "period": params.get("PERI"),
                "amplitude": params.get("AMP"),
                "offset": params.get("OFST"),
                "high_level": params.get("HLEV"),
                "low_level": params.get("LLEV"),
                "phase": params.get("PHSE"),
                "duty_cycle": params.get("DUTY"),
                "pulse_width": params.get("WIDTH"),
                "rise": params.get("RISE"),
                "fall": params.get("FALL"),
                "delay": params.get("DLY"),
            }
            return result_dict[parameter]

        except Exception as e:
            logging.error(f"Failed to retrieve parameter and/or its value: {e}")
            raise

    def set_amplitude(
        self: SiglentSDG1000X,
        channel: int,
        amplitude: Union[float, int],
        unit: AmplitudeUnit = AmplitudeUnit.VPP,
    ) -> None:
        """
        Sets the amplitude for the specified channel on the SiglentSDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            amplitude (Union[float, int]): The amplitude in Vpp, between 0.001 and 20 (High-Z load;
                the instrument allows half of it into 50 Ohm).
            unit (AmplitudeUnit, optional): The unit of the amplitude (default is AmplitudeUnit.VPP).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the amplitude is not a float or int, or if the unit is not an instance of AmplitudeUnit.
            ValueError: If the amplitude is not between 0.001 and 20.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        self._validate_amplitude(amplitude)
        if not isinstance(unit, AmplitudeUnit):
            raise TypeError(
                f"'unit' must be enum of type AmplitudeUnit. Hint: have you forgotten to import 'AmplitudeUnit' from 'pyawg'?"
            )

        try:
            self.write(f"C{channel}:BSWV AMP,{amplitude}")
            logging.debug(f"Channel {channel} amplitude set to {amplitude}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} amplitude to {amplitude}{unit.value}: {e}"
            )
            raise

    def set_burst_cycles(
        self: SiglentSDG1000X, channel: int, cycles: Union[int, str]
    ) -> None:
        """
        Sets the number of cycles emitted per burst for the specified channel on the Siglent SDG1000X.

        Only takes effect while the channel's burst mode is NCYC (see `set_burst_mode`); the
        instrument ignores the cycle count in GATE mode. Burst must be ON (see `set_burst_state`).

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            cycles (int | str): Cycles emitted per trigger, 1 to MAX_BURST_CYCLES, or "INF" for an
                infinite burst.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If cycles is neither an int nor "INF".
            ValueError: If cycles is not between 1 and MAX_BURST_CYCLES.
            RuntimeError: If burst is OFF on the channel.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if cycles != "INF":
            if type(cycles) is not int:
                raise TypeError(f"'cycles' must be int or 'INF'; received {type(cycles)}")
            elif not 1 <= cycles <= self.MAX_BURST_CYCLES:
                raise ValueError(
                    f"'cycles' must be between 1 and {self.MAX_BURST_CYCLES}; received {cycles}"
                )
        self._require_burst_on(channel)

        try:
            self.write(f"C{channel}:BTWV TIME,{cycles}")
            logging.debug(f"Channel {channel} burst cycle count has been set to {cycles}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst cycle count to {cycles}: {e}"
            )
            raise

    def set_burst_delay(
        self: SiglentSDG1000X, channel: int, delay: Union[float, int]
    ) -> None:
        """
        Sets the burst trigger delay for the specified channel on the Siglent SDG1000X.

        Available in NCYC mode only. Burst must be ON (see `set_burst_state`).

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            delay (Union[float, int]): The delay time in seconds (must be non-negative).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the delay is not a float or int.
            ValueError: If the delay is negative.
            RuntimeError: If burst is OFF on the channel.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(delay, (float, int)):
            raise TypeError(f"'delay' must be float or int; received {type(delay)}")
        elif delay < 0:
            raise ValueError(f"'delay' cannot be negative")
        self._require_burst_on(channel)

        try:
            self.write(f"C{channel}:BTWV DLAY,{delay}")
            logging.debug(f"Channel {channel} burst delay has been set to {delay}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst delay to {delay}: {e}"
            )
            raise

    def set_burst_mode(
        self: SiglentSDG1000X, channel: int, burst_mode: BurstModeSiglent
    ) -> None:
        """
        Sets the burst mode for the specified channel on the Siglent SDG1000X.

        Burst must be ON (see `set_burst_state`).

        Args:
            channel (int): The channel number to set the burst mode for. Must be 1 or 2.
            burst_mode (BurstModeSiglent): The burst mode to set. Must be an instance of BurstModeSiglent.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If burst_mode is not an instance of BurstModeSiglent.
            RuntimeError: If burst is OFF on the channel.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(burst_mode, BurstModeSiglent):
            raise TypeError(
                f"'burst_mode' must be enum of type BurstModeSiglent. Hint: have you forgotten to import 'BurstModeSiglent' from 'pyawg'?"
            )
        self._require_burst_on(channel)

        try:
            self.write(f"C{channel}:BTWV GATE_NCYC,{burst_mode.value}")
            logging.debug(
                f"Channel {channel} burst mode has been set to {burst_mode.value}"
            )
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst mode to {burst_mode.value}: {e}"
            )
            raise

    def set_burst_period(
        self: SiglentSDG1000X, channel: int, period: Union[float, int]
    ) -> None:
        """
        Sets the burst period for the specified channel on the Siglent SDG1000X.

        The period only applies with an internal trigger source; with a manual or external trigger
        each burst starts on its trigger. Burst must be ON (see `set_burst_state`).

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            period (Union[float, int]): The burst period in seconds. Must be positive.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the period is not a float or int.
            ValueError: If the period is not positive.
            RuntimeError: If burst is OFF on the channel.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(period, (float, int)):
            raise TypeError(f"'period' must be float or int; received {type(period)}")
        elif period <= 0:
            raise ValueError(f"'period' must be positive")
        self._require_burst_on(channel)

        try:
            self.write(f"C{channel}:BTWV PRD,{period}")
            logging.debug(f"Channel {channel} burst period has been set to {period}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst period to {period}: {e}"
            )
            raise

    def set_burst_run_state(self: SiglentSDG1000X, channel: int, run: bool) -> None:
        """
        Sets the burst playback status (RSTAT) for the specified channel. SDG1000X Plus only.

        With playback stopped the Plus outputs the carrier continuously; RUN makes an armed
        manual/external burst wait for its trigger. Send it after the output is switched on.

        Args:
            channel (int): The channel number. Must be 1 or 2.
            run (bool): True for RUN, False for STOP.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If run is not a boolean.
            UnsupportedModel: If the instrument is not an SDG1000X Plus.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None
        """
        self._validate_channel(channel)
        if type(run) is not bool:
            raise TypeError(f"'run' must be bool; received {type(run)}")
        if "Plus" not in self.model:
            raise UnsupportedModel(self.model, "Burst playback status (RSTAT)")

        state_str = "RUN" if run else "STOP"
        try:
            self.write(f"C{channel}:BURSt:RSTAT {state_str}")
            logging.debug(f"Channel {channel} burst run state has been set to {state_str}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst run state to {state_str}: {e}"
            )
            raise

    def set_burst_state(self: SiglentSDG1000X, channel: int, state: bool) -> None:
        """
        Sets the burst state for the specified channel on the Siglent SDG1000X.

        Must be ON before any other burst parameter is set; enabling it resets them to defaults.

        Args:
            channel (int): The channel number to set the burst state for. Must be 1 or 2.
            state (bool): The desired burst state. True to turn burst on, False to turn it off.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the state is not a boolean.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")

        state_str = "ON" if state else "OFF"
        try:
            self.write(f"C{channel}:BTWV STATE,{state_str}")
            logging.debug(f"Channel {channel} burst state has been set to {state_str}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst state to {state_str}: {e}"
            )
            raise

    def set_burst_trigger_source(
        self: SiglentSDG1000X, channel: int, trigger_source: BurstTriggerSource
    ) -> None:
        """
        Sets the burst trigger source for the specified channel on the Siglent SDG1000X.

        Burst must be ON (see `set_burst_state`).

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            trigger_source (BurstTriggerSource): The burst trigger source, which must be an instance of the BurstTriggerSource enum.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the trigger_source is not an instance of the BurstTriggerSource enum.
            RuntimeError: If burst is OFF on the channel.
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(trigger_source, BurstTriggerSource):
            raise TypeError(
                f"'trigger_source' must be enum of type BurstTriggerSource. Hint: have you forgotten to import 'BurstTriggerSource' from 'pyawg'?"
            )
        self._require_burst_on(channel)

        try:
            self.write(f"C{channel}:BTWV TRSR,{trigger_source.value}")
            logging.debug(
                f"Channel {channel} burst trigger source has been set to {trigger_source.value}"
            )
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} burst trigger source to {trigger_source.value}: {e}"
            )
            raise

    def set_duty_cycle(
        self: SiglentSDG1000X, channel: int, duty_cycle: Union[float, int]
    ) -> None:
        """
        Sets the duty cycle for the specified channel on the Siglent SDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            duty_cycle (Union[float, int]): The duty cycle, which must be either float or int and should be between 0 and 100.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the datatype of duty_cycle is neither float nor int.
            ValueError: If the duty_cycle is not between 0 and 100.
            Exception: If there is an error in writing the duty cycle to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(duty_cycle, (float, int)):
            raise TypeError(
                f"'duty_cycle' must be float or int; received {type(duty_cycle)}"
            )
        elif not (0 <= duty_cycle <= 100):
            raise ValueError(f"'duty_cycle' must be between 0 and 100")

        try:
            self.write(f"C{channel}:BSWV DUTY,{duty_cycle}")
            logging.debug(f"Channel {channel} duty cycle has been set to {duty_cycle}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} duty cycle to {duty_cycle}: {e}"
            )
            raise

    def set_frequency(
        self: SiglentSDG1000X,
        channel: int,
        frequency: Union[float, int],
        unit: FrequencyUnit = FrequencyUnit.HZ,
    ) -> None:
        """
        Sets the frequency for the specified channel on the Siglent SDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            frequency (Union[float, int]): The frequency value to set (must be non-negative).
            unit (FrequencyUnit, optional): The unit of the frequency (default is FrequencyUnit.HZ).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the frequency is not a float or int, or if the unit is not an instance of FrequencyUnit.
            ValueError: If the frequency is negative.
            Exception: If there is an error in writing the frequency to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        self._validate_frequency(frequency)
        if not isinstance(unit, FrequencyUnit):
            raise TypeError(
                f"'unit' must be enum of type FrequencyUnit. Hint: did you forget to import 'FrequencyUnit' from 'pyawg'?"
            )

        try:
            converted_frequency = frequency
            if unit == FrequencyUnit.KHZ:
                converted_frequency = frequency * 1000
            elif unit == FrequencyUnit.MHZ:
                converted_frequency = frequency * 1000000

            self.write(f"C{channel}:BSWV FRQ,{converted_frequency}")
            logging.debug(
                f"Channel {channel} frequency set to {frequency}{unit.value} (converted to {converted_frequency} Hz)"
            )
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} frequency to {frequency}{unit.value}: {e}"
            )
            raise

    def set_offset(
        self: SiglentSDG1000X, channel: int, offset_voltage: Union[float, int]
    ) -> None:
        """
        Sets the offset voltage for the specified channel on the Siglent SDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number to set the offset voltage for. Must be 1 or 2.
            offset_voltage (Union[float, int]): The offset voltage to set. Must be a float or int.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the offset_voltage is not a float or int.
            Exception: If there is an error in writing the offset voltage to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(offset_voltage, (float, int)):
            raise TypeError(
                f"'offset_voltage' must be float or int; received {type(offset_voltage)}"
            )

        try:
            self.write(f"C{channel}:BSWV OFST,{offset_voltage}")
            logging.debug(
                f"Channel {channel} offset voltage set to {offset_voltage} Vdc"
            )
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} offset voltage to {offset_voltage} Vdc: {e}"
            )
            raise

    def set_output(self: SiglentSDG1000X, channel: int, state: bool) -> None:
        """
        Sets the output state of the specified channel on the Siglent SDG1000X.

        Args:
            channel (int): The channel number to set the output state for. Must be 1 or 2.
            state (bool): The desired output state. True for ON, False for OFF.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the state is not a boolean.
            Exception: If there is an error in writing the output state to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")

        state_str = "ON" if state else "OFF"
        try:
            self.write(f"C{channel}:OUTP {state_str}")
            logging.debug(f"Channel {channel} output has been set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output to {state_str}: {e}")
            raise

    def set_output_load(
        self: SiglentSDG1000X, channel: int, load: Union[float, int, OutputLoad]
    ) -> None:
        """
        Set the output load for the specified channel on the Siglent SDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number to set the output load for. Must be 1 or 2.
            load (OutputLoad | int | float): The load value to set. Can be a float, int, or an instance of the OutputLoad enum.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the load is not a float, int, or an instance of OutputLoad.
            Exception: If there is an error in writing the output load to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(load, (float, int, OutputLoad)):
            raise TypeError(
                f"'load' must be float or int or enum of type OutputLoad. Hint: have you forgotten to import 'OutputLoad' from 'pyawg'?"
            )

        if load == OutputLoad.HZ or load == OutputLoad.INF:
            load = "HZ"
        try:
            self.write(f"C{channel}:OUTP LOAD,{load}")
            logging.debug(f"Channel {channel} output load has been set to {load}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output load to {load}: {e}")
            raise

    def set_phase(self: SiglentSDG1000X, channel: int, phase: Union[float, int]) -> None:
        """
        Set the phase of the specified channel on the Siglent SDG1000X.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            phase (Union[float, int]): The phase value to set, in degrees (must be between 0 and 360).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the phase is not a float or int.
            ValueError: If the phase is not between 0 and 360 degrees.
            Exception: If there is an error in writing the phase to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(phase, (float, int)):
            raise TypeError(f"'phase' must be float or int; received {type(phase)}")
        elif not (0 <= abs(phase) <= 360):
            raise ValueError(f"'phase' must be between 0 and 360")

        try:
            self.write(f"C{channel}:BSWV PHSE,{phase}")
            logging.debug(f"Channel {channel} phase set to {phase}°")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} phase to {phase}°: {e}")
            raise

    def set_pulse_width(
        self: SiglentSDG1000X, channel: int, pulse_width: Union[float, int], unit: PulseWidthUnit = PulseWidthUnit.S
    ) -> None:
        """
        Sets the pulse width for the specified channel on the Siglent SDG1000X.

        The width must be shorter than the channel's current period, so set the frequency first.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number (must be 1 or 2).
            pulse_width (Union[float, int]): The pulse width, which must be either float or int.
            unit (PulseWidthUnit): The unit of the pulse width (default is PulseWidthUnit.S).

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the datatype of pulse_width is neither float nor int.
            ValueError: If the pulse_width is not positive or not shorter than the period.
            Exception: If there is an error in writing the pulse width to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(pulse_width, (float, int)):
            raise TypeError(
                f"'pulse_width' must be float or int; received {type(pulse_width)}"
            )
        elif pulse_width <= 0:
            raise ValueError(
                f"'pulse_width' must be positive; received {pulse_width}"
            )

        if not isinstance(unit, PulseWidthUnit):
            raise TypeError(
                f"'unit' must be enum of type PulseWidthUnit. Hint: have you forgotten to import 'PulseWidthUnit' from 'pyawg'?"
            )

        if unit == PulseWidthUnit.mS:
            pulse_width *= 1e-3
        elif unit == PulseWidthUnit.uS:
            pulse_width *= 1e-6

        period = self.get_channel_wave_parameter(channel, "period")
        if period is not None and pulse_width >= float(period.rstrip("S")):
            raise ValueError(
                f"'pulse_width' {pulse_width}s must be shorter than the period {period}"
            )

        try:
            self.write(f"C{channel}:BSWV WIDTH,{pulse_width}")
            logging.debug(f"Channel {channel} pulse width has been set to {pulse_width}s")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} pulse width to {pulse_width}s: {e}"
            )
            raise

    def set_waveform(
        self: SiglentSDG1000X, channel: int, waveform_type: WaveformType
    ) -> None:
        """
        Sets the waveform type for the specified channel.

        Args:
            self (SiglentSDG1000X): The instance of the SiglentSDG1000X class.
            channel (int): The channel number to set the waveform for. Must be 1 or 2.
            waveform_type (WaveformType): The type of waveform to set. Must be an instance of the WaveformType enum.

        Raises:
            InvalidChannelNumber: If the channel number is not 1 or 2.
            TypeError: If the waveform_type is not an instance of WaveformType.
            Exception: If there is an error in writing the waveform type to the device.

        Returns:
            None

        """
        self._validate_channel(channel)
        if not isinstance(waveform_type, WaveformType):
            raise TypeError(
                f"'waveform_type' must be enum of type WaveformType. Hint: have you forgotten to import 'WaveformType' from 'pyawg'?"
            )

        try:
            self.write(f"C{channel}:BSWV WVTP,{waveform_type.value}")
            logging.debug(f"Channel {channel} waveform set to {waveform_type.value}")
        except Exception as e:
            logging.error(
                f"Failed to set channel {channel} waveform to {waveform_type.value}: {e}"
            )
            raise

    def sync_phase(self: SiglentSDG1000X, channel: int = 1) -> None:
        """
        Aligns the phases of both channels (EQPHASE).

        EQPHASE is generator-wide, so `channel` is not used; it is kept only to match the method
        signature of the base class.

        Args:
            channel (int): Unused.

        Raises:
            Exception: If there is an error in writing the command to the device.

        Returns:
            None

        """

        try:
            self.write("EQPHASE")
            logging.debug("Phases of both the channels have been synchronized")
        except Exception as e:
            logging.error(f"Failed to synchronize phase: {e}")
            raise

    def trigger_burst(self: SiglentSDG1000X, channel: int) -> None:
        """
        Triggers a burst on the specified channel of the Siglent SDG1000X signal generator.

        Only valid with a manual trigger source. On an SDG1000X Plus, burst playback must be RUN
        (see `set_burst_run_state`).

        Args:
            channel (int): The channel number to trigger the burst on. Must be 1 or 2.

        Raises:
            InvalidChannelNumber: If the provided channel number is not 1 or 2.
            Exception: If there is an error while sending the trigger command to the device.

        Returns:
            None

        """
        self._validate_channel(channel)

        try:
            self.write(f"C{channel}:BTWV MTRIG")
            logging.debug(f"Burst on channel {channel} has been successfully triggered")
        except Exception as e:
            logging.error(f"Failed to trigger the burst on channel {channel}: {e}")
            raise
