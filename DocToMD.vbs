Dim fso, oShell, scriptDir, result

Set fso    = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
oShell.CurrentDirectory = scriptDir

' Si PyQt6 no esta instalado, mostrar ventana de instalacion y esperar
result = oShell.Run("python -c ""import PyQt6""", 0, True)
If result <> 0 Then
    oShell.Run "cmd /c pip install -r requirements\base.txt && echo. && echo Listo. Cerrando...", 1, True
End If

' Lanzar la app sin ventana de consola
oShell.Run "pythonw -m doctomd", 0, False
