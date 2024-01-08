#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# Author: @m7rick
# Created on: Fri, 8. Jan 2024

import havocui  # type: ignore
import os
import pefile


# Colors
HAVOC_ERROR = "#ff5555"  # Red
HAVOC_SUCCESS = "#50fa7b"  # Green
HAVOC_COMMENT = "#6272a4"  # Greyish blue
HAVOC_DARK = "#555766"  # Dark Grey
HAVOC_INFO = "#8be9fd"  # Cyan
HAVOC_WARNING = "#ffb86c"  # Orange

# Variables & Defaults
Select_language = "GO"
Select_message = "False"
Orginal_DLLPath = ""

# Create dialog and log widget
dialog = havocui.Dialog("DLL Hijacking Tools", True, 670, 300)


# Configuration
OUTPUT_SOURCE_LANGUAGE = ["GO", "CPP"]
SHOW_MESSAGE = ["True","False"]

# Labels
Orginal_label_to_replace = f"<b style=\"color:{HAVOC_ERROR};\">No DLL Path selected.</b>"
Output_Source_Code = f"<b style=\"color:{HAVOC_ERROR};\">Failed to output file.</b>"

def Select_Orginal_DLLPath():
    global Orginal_DLLPath
    global Orginal_label_to_replace

    Orginal_DLLPath = havocui.openfiledialog("Orginal DLL path").decode("ascii")
    print("[*] Orginal DLL Path changed: ", Orginal_DLLPath, ".")

    formatted_OrgDLL_path = f"<span style=\"color:{HAVOC_SUCCESS};\">{Orginal_DLLPath}</span>"
    dialog.replaceLabel(Orginal_label_to_replace, formatted_OrgDLL_path)
    Orginal_label_to_replace = formatted_OrgDLL_path if Orginal_DLLPath != " " \
        else f"<b style=\"color:{HAVOC_ERROR};\">No DLL Path selected.</b>"

def Select_Source_language(num):
    global Select_language
    if num:
        Select_language = OUTPUT_SOURCE_LANGUAGE[num]
    else:
        Select_language = "GO"
    print("[*] Select language method changed: ", Select_language)

def Select_Show_Message(num):
    global Select_message
    if num:
        Select_message = SHOW_MESSAGE[num]
    else:
        Select_message = "False"
    print("[*] Select Show Message method changed: ", Select_message)



Gotemplate = """
package main

import "C"
{function_definitions}

func init(){}

func main(){}
"""


Cpptemplate = """
#include <windows.h>
#define DLLMAIN_API __declspec(dllexport)

{function_definitions}

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        MessageBoxW(0, L"Tips", L"DLLMain", 0);
        break;
	case DLL_THREAD_ATTACH:
	    break;
    case DLL_THREAD_DETACH:
        break;
	case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
"""

def generate_dll_hijack_files(dll_path, code_source,show_message):
    print("[*] DLL Hijack Runing........")
    pe = pefile.PE(dll_path)

    function_definitions_go = ""
    function_definitions_cpp = ""
    for export in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        export_func_name = export.name.decode()

        if code_source == "GO":
            function_definitions_go += "\n//export " + export_func_name + "\nfunc " + export_func_name + "(){}"
        elif code_source == "CPP":
            function_definitions_cpp += "\nextern \"C\" DLLMAIN_API void " + export_func_name + "() \n{"
            if show_message == "True":
                function_definitions_cpp += "\n\tMessageBoxW(0, L\"Tips\", L\"" + export_func_name + "\", 0);"
            function_definitions_cpp += "\n}"

    if code_source == "GO":
        go_code = Gotemplate.replace("{function_definitions}", function_definitions_go)
        with open("DLLHijack.go", "w") as file:
            file.write(go_code)
    elif code_source == "CPP":
        cpp_code = Cpptemplate.replace("{function_definitions}", function_definitions_cpp)
        with open("DLLHijack.cpp", "w") as file:
            file.write(cpp_code)
    
    abs_output_file_path = os.path.abspath(file.name)
    global Output_Source_Code

    formatted_source_code = f"<span style=\"color:{HAVOC_SUCCESS};\">Path : {abs_output_file_path}</span>"
    dialog.replaceLabel(Output_Source_Code, formatted_source_code)
    Output_Source_Code = formatted_source_code if abs_output_file_path != " " \
        else f"<b style=\"color:{HAVOC_ERROR};\">Failed to output file.</b>"

    havocui.messagebox("Tips", "[*] Output path is: "+ abs_output_file_path)


def Run():
    generate_dll_hijack_files(Orginal_DLLPath,Select_language,Select_message)


def DLLHijackingGUI():
    dialog.clear()

    #GUI
    dialog.addLabel(f"<b>──────────────────────────── Required Settings for DLL Hijack ─────────────────────────────</b>")
    dialog.addButton("Original DLL Path", Select_Orginal_DLLPath)
    dialog.addLabel(Orginal_label_to_replace)

    dialog.addLabel("<span style='color:#71e0cb'>[*] Select the language of the output template </span>")
    dialog.addCombobox(Select_Source_language, *OUTPUT_SOURCE_LANGUAGE)

    dialog.addLabel("<span style='color:#71e0cb'>[*] Show message box </span>")
    dialog.addCombobox(Select_Show_Message, *SHOW_MESSAGE)

    dialog.addButton("Generate", Run)
    dialog.addLabel(Output_Source_Code)
    
    dialog.exec()


# Create Tab
havocui.createtab("DLL Hijacking Tools", "Go DLL Hijacking", DLLHijackingGUI)

