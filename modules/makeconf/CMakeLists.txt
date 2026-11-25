# MakeConf view module for Ember Linux
calamares_add_plugin(makeconf
    TYPE viewmodule
    EXPORT_MACRO PLUGINDLLEXPORT_PRO
    SOURCES
        MakeConfViewStep.cpp
    SHARED_LIB
)
