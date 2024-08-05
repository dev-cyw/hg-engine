#include "../include/rtc.h"
#include "../include/save.h"

TIMEOFDAY GF_RTC_GetTimeOfDay(void) {
    struct RTCTime Time;
    u32 VariableTime = GetScriptVar(0x4032);

    switch (VariableTime) {
        case 1: // Morning
            Time.hour = 6;
            break;
        case 2: // Noon
            Time.hour = 12;
            break;
        case 3: // Midnight
            Time.hour = 0;
            break;
        default:
            GF_RTC_CopyTime(&Time);
            break;
    }
    return GF_RTC_GetTimeOfDayByHour(Time.hour);
}
