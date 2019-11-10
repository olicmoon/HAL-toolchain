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

#include <stdint.h>


void Reset_Handler(void)
{
/*    PORT->Group[0].DIRSET.reg = (1u << 17);
    while (1) {
        PORT->Group[0].OUTCLR.reg = (1u << 17);
        for (uint32_t i = 0; i < 10000; ++i) {
            __NOP();
        }
    }
*/
    // First initialize all data from the data section.
    uint32_t *pSrc = &__etext;
    uint32_t *pDest = &__data_start__;
    // If there is data to copy, copy it.
    if ((&__data_start__ != &__data_end__) && (pSrc != pDest)) {
        for (; pDest < &__data_end__; pDest++, pSrc++)
            *pDest = *pSrc;
    }

    // Zero the static variable section.
    if ((&__data_start__ != &__data_end__) && (pSrc != pDest)) {
        for (pDest = &__bss_start__; pDest < &__bss_end__; pDest++)
            *pDest = 0;
    }

    // Call the initialization of the CMSYS library.
    SystemInit();

    // Call our main function, it will never return.
    main();
}

