//
// (c)2019 by Lucky Resistor. See LICENSE for details.
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//


#include "Chip.hpp"

#include <stdbool.h>


const uint8_t cClockMain = 0;
const uint8_t cClockXOSC32K = 1u;
const uint8_t cClockOSC32K = 1u;
const uint8_t cClockOSC8M = 3u;
const uint8_t cClockMuxDFFL48M = 0u;

const uint32_t cCpuSpeed = 48000000u;
const uint32_t cMainOscillatorSpeed = 32768u;


/// Our own implementation of the SystemInit function.
///
void SystemInit()
{
    // Adjust the flash wait state for the new clock.
    NVMCTRL->CTRLB.bit.RWS = NVMCTRL_CTRLB_RWS_HALF_Val;
    // Enable the clock.
    PM->APBAMASK.reg |= PM_APBAMASK_GCLK;
    // Enable the external clock XOSC32K, wait until it stabilized.
    SYSCTRL->XOSC32K.reg = SYSCTRL_XOSC32K_STARTUP(0x6u)|SYSCTRL_XOSC32K_XTALEN|SYSCTRL_XOSC32K_EN32K;
    SYSCTRL->XOSC32K.bit.ENABLE = 1;
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_XOSC32KRDY)==0) {}

    // Do a software reset of the clock module.
    GCLK->CTRL.reg = GCLK_CTRL_SWRST;
    while ((GCLK->CTRL.reg&GCLK_CTRL_SWRST) && (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY)) {}

    // Use XOSC32K as source of clock generator 1
    GCLK->GENDIV.reg = GCLK_GENDIV_ID(cClockXOSC32K);
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}
    GCLK->GENCTRL.reg = GCLK_GENCTRL_ID(cClockOSC32K)|GCLK_GENCTRL_SRC_XOSC32K|GCLK_GENCTRL_GENEN;
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}

    // Use generator 1 as source for the multiplexer DFLL48M and enable it.
    GCLK->CLKCTRL.reg = GCLK_CLKCTRL_ID(cClockMuxDFFL48M)|GCLK_CLKCTRL_GEN_GCLK1|GCLK_CLKCTRL_CLKEN;
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}
    SYSCTRL->DFLLCTRL.reg = SYSCTRL_DFLLCTRL_ENABLE; // bug fix
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLRDY) == 0) {}
    SYSCTRL->DFLLMUL.reg = SYSCTRL_DFLLMUL_CSTEP(0x1fu)|SYSCTRL_DFLLMUL_FSTEP(0x1ffu)|
                           SYSCTRL_DFLLMUL_MUL((cCpuSpeed+cMainOscillatorSpeed/2)/cMainOscillatorSpeed);
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLRDY) == 0) {}
    SYSCTRL->DFLLCTRL.reg |= SYSCTRL_DFLLCTRL_MODE|SYSCTRL_DFLLCTRL_WAITLOCK|SYSCTRL_DFLLCTRL_QLDIS;
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLRDY) == 0) {}
    SYSCTRL->DFLLCTRL.reg |= SYSCTRL_DFLLCTRL_ENABLE;
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLLCKC) == 0||(SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLLCKF) == 0) {}
    while ((SYSCTRL->PCLKSR.reg&SYSCTRL_PCLKSR_DFLLRDY) == 0) {}

    // Now set the main clock to the initialized DFLL48M
    GCLK->GENDIV.reg = GCLK_GENDIV_ID(cClockMain);
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}
    GCLK->GENCTRL.reg = GCLK_GENCTRL_ID(cClockMain)|GCLK_GENCTRL_SRC_DFLL48M|GCLK_GENCTRL_IDC|GCLK_GENCTRL_GENEN;
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}

    // Setup OSC8M
    SYSCTRL->OSC8M.bit.PRESC = SYSCTRL_OSC8M_PRESC_0_Val;
    SYSCTRL->OSC8M.bit.ONDEMAND = 0; // fix
    GCLK->GENDIV.reg = GCLK_GENDIV_ID(cClockOSC8M);
    GCLK->GENCTRL.reg = GCLK_GENCTRL_ID(cClockOSC8M)|GCLK_GENCTRL_SRC_OSC8M|GCLK_GENCTRL_GENEN;
    while (GCLK->STATUS.reg&GCLK_STATUS_SYNCBUSY) {}

    // Enable the clocks on the buses and CPU
    PM->CPUSEL.reg = PM_CPUSEL_CPUDIV_DIV1;
    PM->APBASEL.reg = PM_APBASEL_APBADIV_DIV1_Val;
    PM->APBBSEL.reg = PM_APBBSEL_APBBDIV_DIV1_Val;
    PM->APBCSEL.reg = PM_APBCSEL_APBCDIV_DIV1_Val;

    // Disable automatic NVM writes (for compatibility).
    NVMCTRL->CTRLB.bit.MANW = 1;

    // Enable SysTick at 1kHz/1ms
    if (SysTick_Config(cCpuSpeed/1000)) {
        while (true) {};
    }
    // Lower the priority of the SysTick IRQ down to second lowest (compatibility).
    NVIC_SetPriority(SysTick_IRQn, (1u << __NVIC_PRIO_BITS) - 2);
}

