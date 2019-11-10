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
#include "CoreFunctions.h"
#include "Segments.h"


/// The device vectors.
///
__attribute__((section(".isr_vector"),used))
const DeviceVectors exception_table = {
    (void *) (&__StackTop), // The stack pointer
    (void *) Reset_Handler, // Reset handler
    (void *) NMI_Handler,
    (void *) HardFault_Handler,
    (void *) (0UL),
    (void *) (0UL),
    (void *) (0UL),
    (void *) (0UL),
    (void *) (0UL),
    (void *) (0UL),
    (void *) (0UL),
    (void *) SVC_Handler,
    (void *) (0UL),
    (void *) (0UL),
    (void *) PendSV_Handler,
    (void *) SysTick_Handler,
    (void *) PM_Handler,
    (void *) SYSCTRL_Handler,
    (void *) WDT_Handler,
    (void *) RTC_Handler,
    (void *) EIC_Handler,
    (void *) NVMCTRL_Handler,
    (void *) DMAC_Handler,
    (void *) USB_Handler,
    (void *) EVSYS_Handler,
    (void *) SERCOM0_Handler,
    (void *) SERCOM1_Handler,
    (void *) SERCOM2_Handler,
    (void *) SERCOM3_Handler,
    (void *) SERCOM4_Handler,
    (void *) SERCOM5_Handler,
    (void *) TCC0_Handler,
    (void *) TCC1_Handler,
    (void *) TCC2_Handler,
    (void *) TC3_Handler,
    (void *) TC4_Handler,
    (void *) TC5_Handler,
    (void *) (0UL),
    (void *) (0UL),
    (void *) ADC_Handler,
    (void *) AC_Handler,
    (void *) DAC_Handler,
    (void *) PTC_Handler,
    (void *) I2S_Handler,
    (void *) (0UL),
};


