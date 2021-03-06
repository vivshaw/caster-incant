'''
Created on Sep 1, 2015

@author: synkarius
'''
from dragonfly import Repeat, Function, Key, Text, Dictation, Choice, Mouse, MappingRule

from caster.lib import context, navigation, alphanumeric, textformat
from caster.lib import control
from caster.lib.dfplus.additions import IntegerRefST
from caster.lib.dfplus.merge.ccrmerger import CCRMerger
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.actions import AsynchronousAction, ContextSeeker
from caster.lib.dfplus.state.actions2 import UntilCancelled
from caster.lib.dfplus.state.short import L, S, R
from dragonfly.actions.action_mimic import Mimic
from caster.lib.ccr.standard import SymbolSpecs

_NEXUS = control.nexus()

class NavigationNon(MappingRule):
    mapping = {
        "<direction> <time_in_seconds>":    AsynchronousAction([L(S(["cancel"], Key("%(direction)s"), consume=False))], 
                                                               repetitions=1000, blocking=False ),
        "erase multi clipboard":            R(Function(navigation.erase_multi_clipboard, nexus=_NEXUS), 
                                              rdescript="Erase Multi Clipboard"),
        "find":                             R(Key("c-f"), rdescript="Find"),
        "find next [<n>]":                  R(Key("f3"), rdescript="Find Next") * Repeat(extra="n"),
        "find prior [<n>]":                 R(Key("s-f3"), rdescript="Find Prior") * Repeat(extra="n"),
        "find everywhere":                  R(Key("cs-f"), rdescript="Find Everywhere"),
        "replace":                          R(Key("c-h"), rdescript="Replace"),
        "(F to | F2)":                      R(Key("f2"), rdescript="Key: F2"),
        "(F six | F6)":                     R(Key("f6"), rdescript="Key: F6"),
        "(F nine | F9)":                    R(Key("f9"), rdescript="Key: F9"),
        
        "[show] context menu":              R(Key("s-f10"), rdescript="Context Menu"),
        
        'kick':                             R(Function(navigation.kick, nexus=_NEXUS), rdescript="Mouse: Left Click"),
        'kick mid':                         R(Function(navigation.kick_middle, nexus=_NEXUS), rdescript="Mouse: Middle Click"),
        'psychic':                          R(Function(navigation.kick_right, nexus=_NEXUS), rdescript="Mouse: Right Click"),
        '(kick double|double kick)':        R(Function(navigation.kick, nexus=_NEXUS) * Repeat(2), rdescript="Mouse: Double Click"),
        "shift right click":                R(Key("shift:down") + Mouse("right") + Key("shift:up"), rdescript="Mouse: Shift + Right Click"),
        "curse <direction> [<direction2>] [<nnavi500>] [<dokick>]": R(Function(navigation.curse), rdescript="Curse"),
        "scree <direction> [<nnavi500>]":   R(Function(navigation.wheel_scroll), rdescript="Wheel Scroll"),
      
        "colic":                            R(Key("control:down") + Mouse("left") + Key("control:up"), rdescript="Mouse: Ctrl + Left Click"),
        "garb [<nnavi500>]":                R(Mouse("left")+Mouse("left")+Key("c-c")+Function(navigation.clipboard_to_file, nexus=_NEXUS), rdescript="Highlight @ Mouse + Copy"),
        "drop [<nnavi500>]":                R(Mouse("left")+Mouse("left")+Function(navigation.drop, nexus=_NEXUS), rdescript="Highlight @ Mouse + Paste"),
        
        "cop":                              R(Key("c-c"), rdescript="Simple Copy"),
        "cut":                              R(Key("c-x"), rdescript="Simple Cut"),
        "paish":                            R(Key("c-v"), rdescript="Simple Paste"),
        
        "undo [<n>]":                       R(Key("c-z"), rdescript="Undo") * Repeat(extra="n"),
        "redo [<n>]":                       R(Key("c-y"), rdescript="Redo") * Repeat(extra="n"),

        "refresh":                          R(Key("c-r"), rdescript="Refresh"),
        
        "maxiwin":                          R(Key("w-up"), rdescript="Maximize Window"),
        "move window":                      R(Key("a-space, r, a-space, m"), rdescript="Move Window"),
        "window (left | lease) [<n>]":      R(Key("w-left"), rdescript="Window Left") * Repeat(extra="n"),
        "window (right | ross) [<n>]":      R(Key("w-right"), rdescript="Window Right") * Repeat(extra="n"),
        "monitor (left | lease) [<n>]":     R(Key("sw-left"), rdescript="Monitor Left") * Repeat(extra="n"),
        "monitor (right | ross) [<n>]":     R(Key("sw-right"), rdescript="Monitor Right") * Repeat(extra="n"),
        "(next | prior) window":            R(Key("ca-tab, enter"), rdescript="Next Window"),
        "switch (window | windows)":        R(Key("ca-tab"), rdescript="Switch Window") * Repeat(extra="n"),
        
        "next tab [<n>]":                   R(Key("c-pgdown"), rdescript="Next Tab") * Repeat(extra="n"),
        "prior tab [<n>]":                  R(Key("c-pgup"), rdescript="Previous Tab") * Repeat(extra="n"),
        "close tab [<n>]":                  R(Key("c-w/20"), rdescript="Close Tab") * Repeat(extra="n"),

        "nool <n>":                             R(Key("end, enter"), rdescript="new line") * Repeat(extra="n"),
        
        "[(jump | go to)] line <nlinejump>": R(Key("c-g/5") + Text("%(nlinejump)d") + Key("enter"), rdescript="jump to line"),
          }

    extras   = [
              Dictation("text"),
              Dictation("mim"),
              IntegerRefST("n", 1, 50),
              IntegerRefST("nnavi500", 1, 500),
              IntegerRefST("nlinejump", 0, 1000),
              Choice("time_in_seconds",
                {"super slow": 5, "slow": 2, "normal": 0.6, "fast": 0.1, "superfast": 0.05
                }),
              navigation.get_direction_choice("direction"),
              navigation.get_direction_choice("direction2"),
              navigation.TARGET_CHOICE, 
              Choice("dokick",
                {"kick": 1, "psychic": 2
                }),
              Choice("wm",
                {"ex": 1, "tie": 2
                }),
           ]
    defaults = {
            "n": 1, "mim":"", "nnavi500": 1, "direction2":"", "dokick": 0, "text": "", "wm": 2
           }


class Navigation(MergeRule):
    non = NavigationNon
    pronunciation = CCRMerger.CORE[1]
    
    mapping = {
    # "periodic" repeats whatever comes next at 1-second intervals until "cancel" is spoken or 100 tries occur
    "periodic":                     ContextSeeker(forward=[L(S(["cancel"], lambda: None), \
                                                             S(["*"], \
                                                               lambda fnparams: UntilCancelled(Mimic(*filter(lambda s: s != "periodic", fnparams)), 1).execute(), \
                                                               use_spoken=True))]),
    # VoiceCoder-inspired -- these should be done at the IDE level
    "fill <target>":                R(Key("escape, escape, end"), show=False) +
                                    AsynchronousAction([L(S(["cancel"], Function(context.fill_within_line, nexus=_NEXUS)))
                                                   ], time_in_seconds=0.2, repetitions=50, rdescript="Fill" ),
    "jump in":                      AsynchronousAction([L(S(["cancel"], context.nav, ["right", "(~[~{~<"]))
                                                   ], time_in_seconds=0.1, repetitions=50, rdescript="Jump: In" ),
    "jump out":                     AsynchronousAction([L(S(["cancel"], context.nav, ["right", ")~]~}~>"]))
                                                   ], time_in_seconds=0.1, repetitions=50, rdescript="Jump: Out" ),
    "jump back":                    AsynchronousAction([L(S(["cancel"], context.nav, ["left", "(~[~{~<"]))
                                                   ], time_in_seconds=0.1, repetitions=50, rdescript="Jump: Back" ),
    "jump back in":                 AsynchronousAction([L(S(["cancel"], context.nav, ["left", "(~[~{~<"]))
                                                   ], finisher=Key("right"),
                                                      time_in_seconds=0.1, 
                                                      repetitions=50, 
                                                      rdescript="Jump: Back In" ),
    
    # keyboard shortcuts
    'save this':                         R(Key("c-s"), rspec="save", rdescript="Save"),
    'slap [<nnavi50>]':             R(Key("enter"), rspec="slap", rdescript="Enter") * Repeat(extra="nnavi50"),
    
    "(<mtn_dir> | <mtn_mode> [<mtn_dir>]) [(<nnavi500> | <extreme>)]": R(Function(textformat.master_text_nav), rdescript="Keyboard Text Navigation"),
    
    "sure cop [<nnavi500>]":        R(Key("c-c")+Function(navigation.clipboard_to_file, nexus=_NEXUS), rspec="cop", rdescript="Copy"),
    "sure cut [<nnavi500>]":        R(Key("c-x")+Function(navigation.clipboard_to_file, nexus=_NEXUS), rspec="cut", rdescript="Cut"),
    "sure paish [<nnavi500>]":      R(Function(navigation.drop, nexus=_NEXUS), rspec="paish", rdescript="Paste"),
    
    "kit [<nnavi50>]":              R(Key("del/5"), rspec="kit", rdescript="Delete") * Repeat(extra="nnavi50"),
    "scrip [<nnavi50>]":            R(Key("backspace/5:%(nnavi50)d"), rspec="clear", rdescript="Backspace"),
    "eat [<nnavi50>] [<mtn_dir>]":  R(Key("cs-%(mtn_dir)s/5:%(nnavi50)d") + Key("backspace"), rdescript="delete by word"),
    SymbolSpecs.CANCEL:             R(Key("escape"), rspec="cancel", rdescript="Cancel Action"),
    
    
    "shackle":                      R(Key("home/5, s-end"), rspec="shackle", rdescript="Select Line"),
    "(tell | tau) <semi>":          R(Function(navigation.next_line), rspec="tell dock", rdescript="Complete Line"), 
    "duple [<nnavi50>]":            R(Key("escape, home, s-end, c-c, end, enter, c-v"), rspec="duple", rdescript="Duplicate Line") * Repeat(extra="nnavi50"),
    "Kraken":                       R(Key("c-space"), rspec="Kraken", rdescript="Control Space"),

    "whack":                        R(Key("end, semicolon, enter"), rdescript="End line with semicolon & enter"),
    "wig":                          R(Key("end, semicolon"), rdescript="End line with semicolon"),
    "sweep":                        R(Key("end, comma, enter"), rdescript="End line with comma & enter"),
    "brute":                        R(Key("end, space, lbrace, enter"), rdescript="End line with brace block"),
         
    # text formatting
    "set format (<capitalization> <spacing> | <capitalization> | <spacing>)":  R(Function(textformat.set_text_format), rdescript="Set Text Format"),
    "clear caster formatting":      R(Function(textformat.clear_text_format), rdescript="Clear Caster Formatting"),
    "peek format":                  R(Function(textformat.peek_text_format), rdescript="Peek Format"),
    "(<capitalization> <spacing> | <capitalization> | <spacing>) <textnv> [brunt]":  R(Function(textformat.master_format_text), rdescript="Text Format"),
    "format <textnv>":              R(Function(textformat.prior_text_format), rdescript="Last Text Format"),
    "dredge":                       R(Key("a-tab"), rdescript="Alt-Tab"),
    "<textnv>":                     R(Function(textformat.master_format_text), rdescript="Default dictation format"),

    # term cmds
    "term paish":                   R(Key("s-insert"), rdescript="Paste into term"),

    # tab cmds
    "next tab [<nnavi50>]":         R(Key("c-tab"), rdescript="next tab") * Repeat(extra="nnavi50"),
    "last tab [<nnavi50>]":         R(Key("cs-tab"), rdescript="last tab") * Repeat(extra="nnavi50"),
    }

    extras = [
        IntegerRefST("nnavi50", 1, 50),
        IntegerRefST("nnavi500", 1, 500),
        Dictation("textnv"),
        
        Choice("capitalization",
                  {"yell": 1, "tie": 2,"grish": 3,"sing":4, "laws":5
                  }),
        Choice("spacing",
                  {"gum": 1, "gun": 1, "spine": 2, "snake":3
                  }),
        Choice("semi",
                    {"dock": ";", "doc": ";", "sink": ""
                    }),
          
          
          
        navigation.TARGET_CHOICE,
        navigation.get_direction_choice("mtn_dir"),
        Choice("mtn_mode",
                {"shin": "s", "queue": "cs", "fly": "c",
                }),
        Choice("extreme",
                {"way": "way",
                }),
    ]

    defaults ={
            "nnavi500": 1, "nnavi50": 1, "textnv": "", "capitalization": 0, "spacing":0, 
            "mtn_mode": None, "mtn_dir": "left", "extreme": None 
           }

control.nexus().merger.add_global_rule(Navigation())