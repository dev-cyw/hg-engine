import sys
import os
import struct
import shutil

"""
idea here is to autogenerate a makefile to be included by the main Makefile that is a massive list of target:src run this command

data/graphics/species_name/gender/*.png
backf backm frontf frontm normal shiny

output
build/pokemonpic/index-00.NCGR
build/pokemonpic/index-01.NCGR
build/pokemonpic/index-02.NCGR
build/pokemonpic/index-03.NCGR
build/pokemonpic/index-04.NCLR
build/pokemonpic/index-05.NCLR
"""

dump = False

def GrabSpeciesDict(speciesDict: dict):
    speciesEntry = 0
    with open("include/constants/species.h") as f:
        for line in f:
            if len(line.split()) > 1:
                test = line.split()[1].strip()
                if 'SPECIES' in test and not '_START' in test and not '_SPECIES_H' in test and not '_NUM (' in line and not 'MAX_' in test:
                    if dump:
                        speciesDict[speciesEntry] = test
                    else:
                        speciesDict[test] = speciesEntry
                    speciesEntry += 1

"""
entry template:

SPECIES_NIDORAN_M corresponds to
data/graphics/nidoran_m
-> male
  -> front.png
  -> back.png
-> female
  -> front.png
  -> back.png
-> icon.png

i.e.
SPECIES_522 corresponds to...
data/graphics/522
"""


ncgr_gen_format = """	$(GFX) $< $@ $(POKEGRA_GFX_FLAGS_SPRITE)
"""
nclr_front_gen_format = """	if test -s $<; then \\
		$(GFX) $< $@ $(POKEGRA_GFX_FLAGS_PAL); \\
	elif test -s $(patsubst $(POKEGRA_SPRITES_DIR)/%/male/front.png,$(POKEGRA_SPRITES_DIR)/%/female/front.png,$<); then \\
		$(GFX) $(patsubst $(POKEGRA_SPRITES_DIR)/%/male/front.png,$(POKEGRA_SPRITES_DIR)/%/female/front.png,$<) $@ $(POKEGRA_GFX_FLAGS_PAL); \\
	fi
"""
nclr_back_gen_format = """	if test -s $<; then \\
		$(GFX) $< $@ $(POKEGRA_GFX_FLAGS_PAL); \\
	elif test -s $(patsubst $(POKEGRA_SPRITES_DIR)/%/male/back.png,$(POKEGRA_SPRITES_DIR)/%/female/back.png,$<); then \\
		$(GFX) $(patsubst $(POKEGRA_SPRITES_DIR)/%/male/back.png,$(POKEGRA_SPRITES_DIR)/%/female/back.png,$<) $@ $(POKEGRA_GFX_FLAGS_PAL); \\
	fi
POKEGRA_DEPENDENCIES += {0}-00.NCGR {0}-01.NCGR {0}-02.NCGR {0}-03.NCGR {0}-04.NCLR {0}-05.NCLR
"""
icon_format = """\t$(GFX) $< $@ -clobbersize -version101

ICONGFX_OBJS += {0}.NCGR


"""


"""
path_resolver takes an input file and tries to determine the species name from it so it can 
return the output path.  this output path is then fed to nitrogfx to build proper for narc packing
"""
def path_resolver(inputPath: str, speciesDict: dict) -> str:
    if "data/graphics/sprites/" in inputPath:
        inputPath = inputPath[len("data/graphics/sprites/"):]

    speciesName = "SPECIES_" + inputPath.upper()

    inputPath = "build/pokemonpic/{:04d}".format(speciesDict[speciesName])
    
    return inputPath


def path_resolver_icons(inputPath: str, speciesDict: dict) -> str:
    if "data/graphics/icongfx/" in inputPath:
        inputPath = inputPath[len("data/graphics/icongfx/"):]

    speciesName = "SPECIES_" + inputPath.upper()

    inputPath = "build/pokemonicon/1_{:04d}".format(speciesDict[speciesName])
    
    return inputPath


def GenMakefile(outputPath: str, speciesDict: dict):
    output = open(outputPath, "w")
# header
    output.write("""# DO NOT MODIFY THIS FILE!  autogenerated by scripts/reformat_sprite_data.py

POKEGRA_DIR := data/graphics
POKEGRA_SPRITES_DIR := $(POKEGRA_DIR)/sprites
POKEGRA_BUILD_DIR := $(BUILD)/pokemonpic
POKEGRA_NARC := $(BUILD_NARC)/pokegra.narc
POKEGRA_TARGET := $(FILESYS)/a/0/0/4
PBR_POKEGRA_TARGET := $(FILESYS)/pbr/pokegra.narc

POKEGRA_GFX_FLAGS_SPRITE := -scanfronttoback -handleempty
POKEGRA_GFX_FLAGS_PAL := -bitdepth 8 -nopad -comp 10


ICONGFX_DIR := $(BUILD)/pokemonicon
ICONGFX_NARC := $(BUILD_NARC)/pokemonicon.narc
ICONGFX_TARGET := $(FILESYS)/a/0/2/0
ICONGFX_DEPENDENCIES_DIR := data/graphics/icongfx
ICONGFX_RAWDATA_DIR := rawdata/files_from_a020


""")

# entries
    for entry in speciesDict:
        speciesName = entry[len("SPECIES_"):].lower()
        convertedName = path_resolver(speciesName, speciesDict)
        convertedIcon = path_resolver_icons(speciesName, speciesDict)
        output.write(convertedName + "-00.NCGR: data/graphics/sprites/" + speciesName + "/female/back.png\n" + ncgr_gen_format)
        output.write(convertedName + "-01.NCGR: data/graphics/sprites/" + speciesName + "/male/back.png\n" + ncgr_gen_format)
        output.write(convertedName + "-02.NCGR: data/graphics/sprites/" + speciesName + "/female/front.png\n" + ncgr_gen_format)
        output.write(convertedName + "-03.NCGR: data/graphics/sprites/" + speciesName + "/male/front.png\n" + ncgr_gen_format)
        output.write(convertedName + "-04.NCLR: data/graphics/sprites/" + speciesName + "/male/front.png\n" + nclr_front_gen_format)
        output.write(convertedName + "-05.NCLR: data/graphics/sprites/" + speciesName + "/male/back.png\n" + nclr_back_gen_format.format(convertedName))
        output.write(convertedIcon + ".NCGR: data/graphics/sprites/" + speciesName + "/icon.png\n" + icon_format.format(convertedIcon))

# footer
    output.write("""$(POKEGRA_NARC): $(POKEGRA_DEPENDENCIES)
	$(NARCHIVE) create $@ $(POKEGRA_BUILD_DIR) -nf

NARC_FILES += $(POKEGRA_NARC)

$(ICONGFX_NARC): $(ICONGFX_OBJS)
	cp -r $(ICONGFX_RAWDATA_DIR)/. $(ICONGFX_DIR)
	$(NARCHIVE) create $@ $(ICONGFX_DIR) -nf

NARC_FILES += $(ICONGFX_NARC)

""")


def ConvertExistingRepo(speciesDict: dict, entryDict: dict):
    for entry in entryDict:
        #print("{:04d}".format(entry), entryDict[entry].lower()[len("SPECIES_"):])
        if os.path.isdir("data/graphics/sprites/" + entryDict[entry].lower()[len("SPECIES_"):]):
            shutil.rmtree("data/graphics/sprites/" + entryDict[entry].lower()[len("SPECIES_"):])
        os.rename("data/graphics/sprites/{:04d}".format(entry), "data/graphics/sprites/" + entryDict[entry].lower()[len("SPECIES_"):])
        if os.path.exists("data/graphics/sprites/{0}/icon.png".format(entryDict[entry].lower()[len("SPECIES_"):])):
            os.remove("data/graphics/sprites/{0}/icon.png".format(entryDict[entry].lower()[len("SPECIES_"):]))
        os.rename("data/graphics/icongfx/{:04d}.png".format(entry), "data/graphics/sprites/{0}/icon.png".format(entryDict[entry].lower()[len("SPECIES_"):]))

if __name__ == '__main__':
    speciesDict = {}
    entryDict = {}
    args = sys.argv[1:]
    if (len(args) == 1):
        GrabSpeciesDict(speciesDict)
        GenMakefile(args[0].strip(), speciesDict)
    elif '--convert' in args[0]:
        dump = True
        GrabSpeciesDict(entryDict)
        dump = False
        GrabSpeciesDict(speciesDict)
        ConvertExistingRepo(speciesDict, entryDict)
        GenMakefile(args[1].strip(), speciesDict)
