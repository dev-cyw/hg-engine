#include "../include/types.h"
#include "../include/script.h"
#include "../include/constants/item.h"
#include "../include/bag.h"


// script command 0xD0, DummyTextTrap/scrcmd_208
u32 ScrCmd_Custom_Scripts(SCRIPTCONTEXT *ctx)
{
    u32 sw = ScriptReadByte(ctx);
    u32 arg0 = ScriptReadHalfword(ctx);

    switch(sw) {
        case 0: { //Give Pokemon An item
            u16 PartySlot = GetScriptVar(0x8004);
            u16 ItemId = GetScriptVar(0x8005);

            FieldSystem *fieldSystem = ctx->fsys;
            struct PartyPokemon *partyMon;
            struct Party *party = SaveData_GetPlayerPartyPtr(fieldSystem->savedata);
            partyMon = Party_GetMonByIndex(party, PartySlot);

            u16 HeldItem = GetMonData(partyMon, MON_DATA_HELD_ITEM, NULL);
            if (HeldItem != ITEM_NONE) {
                BAG_DATA *bag = Sav2_Bag_get(fieldSystem->savedata);
                Bag_AddItem(bag, HeldItem, 1, 11);
            }
            SetMonData(partyMon, MON_DATA_HELD_ITEM, &ItemId);
            break;
        }
        case 1: {

            break;
        }
    }
    return 0;
}
