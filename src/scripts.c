#include "../include/types.h"
#include "../include/script.h"
#include "../include/constants/item.h"
#include "../include/bag.h"
#include "../include/battle.h"

// script command 0xD0, DummyTextTrap/scrcmd_208
u32 ScrCmd_Custom_Scripts(SCRIPTCONTEXT *ctx)
{
    u32 sw = ScriptReadByte(ctx);
    u32 arg0 = ScriptReadHalfword(ctx);

    switch(sw) {
        case 0: { // Give Pokemon An item
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
        case 1: { // Pre-Status a Mon
            u16 PartySlot = GetScriptVar(0x8004);
            u16 StatusId = GetScriptVar(0x8005);
            u16 Status;

            FieldSystem *fieldSystem = ctx->fsys;
            struct PartyPokemon *partyMon;
            struct Party *party = SaveData_GetPlayerPartyPtr(fieldSystem->savedata);
            partyMon = Party_GetMonByIndex(party, PartySlot);

            switch(StatusId){
                case 0:
                    Status = STATUS_FLAG_BURNED;
                    break;
                case 1:
                    Status = STATUS_FLAG_POISONED;
                    break;
                case 2:
                    Status = STATUS_FLAG_PARALYZED;
                    break;
                default:
                    Status = 0;
                    break;
            }
            SetMonData(partyMon, MON_DATA_STATUS, &Status);
            break;
        }
        case 2: { // Pre-Damage
            u16 PartySlot = GetScriptVar(0x8004);
            u16 DamageId = GetScriptVar(0x8005);

            FieldSystem *fieldSystem = ctx->fsys;
            struct PartyPokemon *partyMon;
            struct Party *party = SaveData_GetPlayerPartyPtr(fieldSystem->savedata);
            partyMon = Party_GetMonByIndex(party, PartySlot);

            u16 hp = GetMonData(partyMon, MON_DATA_HP, NULL);
            u16 damageValues[] = {100, 50, 25, 10, 5, 1};

            if (DamageId >= 0 && DamageId <= 4) {
                u16 damage = damageValues[DamageId];

                if (hp <= damage) {
                    hp = 1;
                } else {
                    hp -= damage;
                }
            }

            SetMonData(partyMon, MON_DATA_HP, &hp);
            break;
        }
        case 3: { // Weather Effects

            break;
        }
    }
    return 0;
}
