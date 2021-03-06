import pyjadx
import frida
import pygments
import os

# TODO 2020. 02. 25. JVM Error Handling
# TODO 2020. 02. 26. Package Name Auto Detection
# TODO 2020. 02. 26. Java Object Memory Address Checking
# @param pyjadx.Jadx $app Decompiled APK or Dex Object
def hasRootCheck(app): 
    AntiRootList = set()

    # Rooting check files
    rootFiles = [
            '/sbin/su', '/system/su',
            '/system/bin/su', '/system/sbin/su',
            '/system/xbin/su', '/system/xbin/mu',
            '/system/bin/.ext/.su', '/system/usr/su-backup',
            '/data/data/com.noshufou.android.su', '/system/app/Superuser.apk',
            '/system/app/su.apk', '/system/bin/.ext',
            '/system/xbin/.ext', '/data/local/xbin/su',
            '/data/local/bin/su', '/system/sd/xbin/su',
            '/system/bin/failsafe/su', '/data/local/su',
            '/su/bin/su', 'busybox', 'Emulator'
        ]

    if app.classes: # Can code dumping?
        dump_path = input("class founded, where I save it? : android-auto-hack/dump-code/")
        dump_path = './dump-code/' + dump_path
        try:
            if not os.path.isdir(dump_path):
                os.mkdir(dump_path)
        except Exception as e:
            print(e)
    
    # Extract root checker classes
    for cls in app.classes:
        if ('google' in cls.fullname) or ('android' in cls.fullname) or ('kakao' in cls.fullname) or ('facebook' in cls.fullname) or ('naver' in cls.fullname): # optimization
            continue
        else:
            cls.save(dump_path + '/' + cls.fullname + '.java') # code dump -> generate cahce
            target_code_line = cls.code.splitlines()
            for rootfile in rootFiles:
                for iter in target_code_line:
                    if rootfile in iter:
                        AntiRootList.add(cls.fullname)
                        break

    return AntiRootList

# @param pyjadx.Jadx $app Decompiled APK or Dex Object
def MakeBypassScript(app):
    jscode = ""
    AntiRootList = hasRootCheck(app)
    
    # Anti-Root Detected
    if AntiRootList:
        jscode += '/* Rooting Bypass */\n'
        jscode += 'console.log("[*] Bypass Anti-Root Start...");\n'
        for i in AntiRootList: # Classes
            for j in app.get_class(i).methods: # Methods
                if (str(j.return_type) == 'boolean'): # if Methods return type is bool and equal root check method
                    jscode += 'try {\n'
                    jscode += f'    Java.use("{i}").{j.name}.implementation = function()'
                    jscode += ' {    try {   return false;   } catch(e) {    return this.' + j.name + '();   }   }\n'
                    jscode += '} catch(e) {    console.error(e);   }\n\n' # fix overload issue
        return jscode # java.lang.ClassNotFoundException
    # No Root Checker
    else:
        print("[*] Anti-Root no exist")
        return None