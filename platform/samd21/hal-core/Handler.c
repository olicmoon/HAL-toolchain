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


/// An empty default handler which just blocks the CPU.
///
void Default_Handler(void)
{
    while (true) {}
}

/// A default handler with a weak link.
///
#define LR_DEFAULT_HANDLER(handlerName) void handlerName(void) __attribute__ ((weak, alias("Default_Handler")));

/// A static handler which is implemented in the core
///
#define LR_STATIC_HANDLER(handlerName) void handlerName(void);

// Core Handlers for Cortex-M0+
LR_DEFAULT_HANDLER(HardFault_Handler);
LR_STATIC_HANDLER(Reset_Handler);
LR_DEFAULT_HANDLER(NMI_Handler);
LR_DEFAULT_HANDLER(SVC_Handler);
LR_DEFAULT_HANDLER(PendSV_Handler);
LR_STATIC_HANDLER(SysTick_Handler);

// Handlers for all Peripherals of SAM D21
LR_DEFAULT_HANDLER(PM_Handler);
LR_DEFAULT_HANDLER(SYSCTRL_Handler);
LR_DEFAULT_HANDLER(WDT_Handler);
LR_DEFAULT_HANDLER(RTC_Handler);
LR_DEFAULT_HANDLER(EIC_Handler);
LR_DEFAULT_HANDLER(NVMCTRL_Handler);
LR_DEFAULT_HANDLER(DMAC_Handler);
LR_DEFAULT_HANDLER(USB_Handler);
LR_DEFAULT_HANDLER(EVSYS_Handler);
LR_DEFAULT_HANDLER(SERCOM0_Handler);
LR_DEFAULT_HANDLER(SERCOM1_Handler);
LR_DEFAULT_HANDLER(SERCOM2_Handler);
LR_DEFAULT_HANDLER(SERCOM3_Handler);
LR_DEFAULT_HANDLER(SERCOM4_Handler);
LR_DEFAULT_HANDLER(SERCOM5_Handler);
LR_DEFAULT_HANDLER(TCC0_Handler);
LR_DEFAULT_HANDLER(TCC1_Handler);
LR_DEFAULT_HANDLER(TCC2_Handler);
LR_DEFAULT_HANDLER(TC3_Handler);
LR_DEFAULT_HANDLER(TC4_Handler);
LR_DEFAULT_HANDLER(TC5_Handler);
LR_DEFAULT_HANDLER(TC6_Handler);
LR_DEFAULT_HANDLER(TC7_Handler);
LR_DEFAULT_HANDLER(ADC_Handler);
LR_DEFAULT_HANDLER(AC_Handler);
LR_DEFAULT_HANDLER(DAC_Handler);
LR_DEFAULT_HANDLER(PTC_Handler);
LR_DEFAULT_HANDLER(I2S_Handler);
