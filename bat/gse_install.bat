@echo off

setlocal EnableDelayedExpansion
set cu_date=%date:~0,4%-%date:~5,2%-%date:~8,2%
set cu_time=%time:~0,8%

set local_ip=
set cloud_id=
set proxy_out_ip=
set proxy_in_ip=
set biz_id=
set data_ip=
set conn_ip=
set gse_install_path=
set service_id=

rem 传参函数，实现多个输入开关
:CheckOpts
if "%1" EQU "-h" goto Help
if "%1" EQU "-o" (set local_ip=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-i" (set cloud_id=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-w" (set proxy_out_ip=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-l" (set proxy_in_ip=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-I" (set biz_id=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-D" (set data_ip=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-E" (set conn_ip=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-p" (set gse_install_path=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-s" (set service_id=%~2) && shift && shift && goto CheckOpts
if "%1" EQU "-r" goto remove_gse_agent
if "%1" NEQ "" echo Invalid option: "%1" && goto :EOF && exit /B 1
if "%1" NEQ "-r" goto install_gse_agent

:remove_gse_agent
if not defined local_ip (set local_ip=) else (set local_ip=%local_ip%)
if not defined cloud_id (set cloud_id=0) else (set cloud_id=%cloud_id%)
if not defined proxy_out_ip (set proxy_out_ip=) else (set proxy_out_ip=%proxy_out_ip%)
if not defined proxy_in_ip (set proxy_in_ip=) else (set proxy_in_ip=%proxy_in_ip%)
if not defined biz_id (set biz_id=) else (set biz_id=%biz_id%)
if not defined data_ip (set data_ip=) else (set data_ip=%data_ip%)
if not defined conn_ip (set conn_ip=) else (set conn_ip=%conn_ip%)
if not defined gse_install_path (set gse_install_path=C:\\gse) else (set gse_install_path=%gse_install_path%)
if "%service_id%" EQU "default" (set service_id=) else (set service_id=%service_id%)
if not defined service_id (set _service_id=) else (set _service_id=_%service_id%)
set special_gse_install_path=%gse_install_path%
set special_gse_install_path=%special_gse_install_path:\=\\%

	if "%local_ip%" == "" (
		echo [%local_ip%] %cu_date% %cu_time% -- local_ip get fail
		goto :EOF
	)

    rem 强杀老版本进程
    sc query gseDaemon | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
        sc stop gseDaemon 1>nul 2>&1
        ping -n 2 127.0.0.1 1>nul 2>&1
        sc delete gseDaemon 1>nul 2>&1
        ping -n 2 127.0.0.1 1>nul 2>&1
        taskkill /im gse_win_agent.exe /im gse_win_daemon.exe /im basereport.exe /im bkmetricbeat.exe /im gsecmdline.exe /im processbeat.exe /f 1>nul 2>&1
        ping -n 2 127.0.0.1 1>nul 2>&1
		del /Q /S /F C:\gse >>error.log 1>nul 2>&1
		rd /Q /S C:\gse >>error.log 1>nul 2>&1
		rm -rf C:\gse >>error.log 1>nul 2>&1
    )

    rem 判断gse是否已经安装，如果已经安装则删除
	sc query gse_agent_daemon%_service_id% | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
		cd /d %gse_install_path%\agent\bin
		rem 停止进程
		if not exist %cd:~0,-9%.service_id (set _service_id=) else (set /p service_id=<%cd:~0,-9%.service_id && set _service_id=_%service_id%)
		gse_agent_daemon.exe --quit --name gse_agent_daemon%_service_id% 1>nul 2>&1
        ping -n 3 127.0.0.1 1>nul 2>&1
        sc delete gse_agent_daemon%_service_id% >>error.log 1>nul 2>&1
        ping -n 3 127.0.0.1 1>nul 2>&1
		wmic process where "name='gse_agent_daemon.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent_daemon.exe'" call terminate 1>nul 2>&1
		wmic process where "name='gse_agent.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent.exe'" call terminate 1>nul 2>&1
		wmic process where "name='basereport.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\basereport.exe'" call terminate 1>nul 2>&1
		wmic process where "name='bkmetricbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\bkmetricbeat.exe'" call terminate 1>nul 2>&1
		wmic process where "name='gsecmdline.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\gsecmdline.exe'" call terminate 1>nul 2>&1
		wmic process where "name='processbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\processbeat.exe'" call terminate 1>nul 2>&1
        ping -n 3 127.0.0.1 1>nul 2>&1
    )

    rem 删除目录
    set install_dir=%~dp0
    cd /d %install_dir%
    if exist %gse_install_path% (
		del /Q /S /F %gse_install_path% >>error.log 1>nul 2>&1
		rd /Q /S %gse_install_path% >>error.log 1>nul 2>&1
        if exist %gse_install_path% (
			wmic process where "name='gse_agent_daemon.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent_daemon.exe'" call terminate 1>nul 2>&1
			wmic process where "name='gse_agent.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent.exe'" call terminate 1>nul 2>&1
			wmic process where "name='basereport.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\basereport.exe'" call terminate 1>nul 2>&1
			wmic process where "name='bkmetricbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\bkmetricbeat.exe'" call terminate 1>nul 2>&1
			wmic process where "name='gsecmdline.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\gsecmdline.exe'" call terminate 1>nul 2>&1
			wmic process where "name='processbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\processbeat.exe'" call terminate 1>nul 2>&1
            ping -n 3 127.0.0.1 1>nul 2>&1
			del /Q /S /F %gse_install_path% >>error.log 1>nul 2>&1
			rd /Q /S %gse_install_path% >>error.log 1>nul 2>&1
			rm -rf %gse_install_path% >>error.log 1>nul 2>&1
			del /Q /S /F C:\gse >>error.log 1>nul 2>&1
			rd /Q /S C:\gse >>error.log 1>nul 2>&1
			rm -rf C:\gse >>error.log 1>nul 2>&1
            if exist %gse_install_path% (
			wmic process where "name='gse_agent_daemon.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent_daemon.exe'" call terminate 1>nul 2>&1
			wmic process where "name='gse_agent.exe' and ExecutablePath='%special_gse_install_path%\\agent\\bin\\gse_agent.exe'" call terminate 1>nul 2>&1
			wmic process where "name='basereport.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\basereport.exe'" call terminate 1>nul 2>&1
			wmic process where "name='bkmetricbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\bkmetricbeat.exe'" call terminate 1>nul 2>&1
			wmic process where "name='gsecmdline.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\gsecmdline.exe'" call terminate 1>nul 2>&1
			wmic process where "name='processbeat.exe' and ExecutablePath='%special_gse_install_path%\\plugins\\bin\\processbeat.exe'" call terminate 1>nul 2>&1
            ping -n 3 127.0.0.1 1>nul 2>&1
			del /Q /S /F %gse_install_path% >>error.log 1>nul 2>&1
			rd /Q /S %gse_install_path% >>error.log 1>nul 2>&1
			rm -rf %gse_install_path% >>error.log 1>nul 2>&1
			del /Q /S /F C:\gse >>error.log 1>nul 2>&1
			rd /Q /S C:\gse >>error.log 1>nul 2>&1
			rm -rf C:\gse >>error.log 1>nul 2>&1
            )
        )
    )

    rem 判断是否删除成功
    sc query gse_agent_daemon%_service_id% | findstr /i "SERVICE_NAME" 1>nul 2>null
		if !errorlevel! neq 0 (
        sc delete gse_agent_daemon%_service_id% >>error.log 1>nul 2>&1
		)

	call :remove_gse_install_path
	ping -n 3 127.0.0.1 1>nul 2>&1

    rem 老版本进程判断是否删除成功
    sc query gseDaemon | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- gseDaemon service delete fail/install gseagent
        goto :EOF
    )

    rem 新版本进程判断是否删除成功
    sc query gse_agent_daemon%_service_id% | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- service delete fail/install gseagent
        goto :EOF
    )

    if exist %gse_install_path% (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- %gse_install_path% folder delete fail/uninstall gseagent
        goto :EOF
    ) else (
        echo [%local_ip%] %cu_date% %cu_time% uninstall done -- uninstall done/uninstall gseagent
        goto :EOF
    )
)

goto :EOF

:install_gse_agent
call :remove_gse_agent
    if "%biz_id%" == "" (
        set biz_id=0
    )

    if "%local_ip%" == "" (
        echo [%local_ip%] %cu_date% %cu_time% local_ip get fail
        goto :EOF
    )

    if "%cloud_id%" == "" (
        echo [%local_ip%] %cu_date% %cu_time% cloud_id get fail
        goto :EOF
    )

    rem 老版本进程判断是否删除成功
    sc query gseDaemon | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- gseDaemon service delete fail/install gseagent
        goto :EOF
    )

    rem 新版本进程判断是否删除成功
    sc query gse_agent_daemon%_service_id% | findstr /i "SERVICE_NAME" 1>nul 2>&1
    if !errorlevel! equ 0 (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- service delete fail/install gseagent
        goto :EOF
    )

    if exist %gse_install_path% (
        echo [%local_ip%] %cu_date% %cu_time% uninstall failed -- %gse_install_path% folder delete fail/install gseagent
        goto :EOF
    )

    if "%PROCESSOR_ARCHITECTURE%" == "x86" (
        set pkg_name="gse_client-windows-x86"
    ) else (
        set pkg_name="gse_client-windows-x86_64"
    )

    rem 设置安装目录
    set install_dir=%~dp0
    cd /d %install_dir%
    ..\7z.exe x ../%pkg_name%.tgz -y >>error.log 1>nul 2>&1
    if not exist %pkg_name%.tar (
        echo [%local_ip%] %cu_date% %cu_time% setup failed -- %pkg_name%_64.tgz unzip tar file fail/install gseagent
        goto :EOF
    )
    md %gse_install_path%
    ..\7z.exe x %pkg_name%.tar -o%gse_install_path% -y >>error.log 1>nul 2>&1
	if not defined service_id (set _service_id=) else (echo %service_id% > %gse_install_path%\.service_id && sed -i "/^\s*$/d" %gse_install_path%\.service_id 1>nul 2>&1)
    if not exist %gse_install_path%\agent\bin\gse_agent_daemon.exe (
        echo [%local_ip%] %cu_date% %cu_time% setup failed -- %pkg_name%_64.tgz unzip gse dir fail/install gseagent
        goto :EOF
    )

    rem 定义修改配置文件
    set conf_file=%gse_install_path%\agent\etc\iagent.conf
    set relese_conf_file=%gse_install_path%\agent\etc\agent.conf
    set noncygwin_conf=%gse_install_path%\agent\etc\procinfo_noncygwin.json
    set procinfo_conf=%gse_install_path%\agent\etc\procinfo.json
    copy %noncygwin_conf% %procinfo_conf% /y >>error.log 1>nul 2>&1

	rem cloud_id若不定义，即没有-i参数时，cloud_id设置为0（直连区域）
	rem cloud_id若定义，有-i参数时，cloud_id设置为传入的参数值（云区域）
	rem 当cloud_id没有定义，或者为0时，只替换agent.conf的@@AGENT_LAN_IP及@@EXTERNAL_IP@@，并判断这2个替换后是否为空，为空失败
	if defined cloud_id (
		if "%cloud_id%" NEQ "0" (
			rem 复制配置文件
			copy %conf_file% %relese_conf_file% /y >>error.log 1>nul 2>&1

			rem 替换agent.conf，iagent.conf的@@AGENT_LAN_IP，@@EXTERNAL_IP@@，@@BIZ_ID@@，@@CLOUD_ID@@配置
			sed -i "s/@@BIZ_ID@@/%biz_id%/g" %conf_file% 1>nul 2>&1
			sed -i "s/@@CLOUD_ID@@/%cloud_id%/g" %conf_file% 1>nul 2>&1
			sed -i "s/@@AGENT_LAN_IP@@/%conn_ip%/g" %conf_file% 1>nul 2>&1
			sed -i "s/@@EXTERNAL_IP@@/%data_ip%/g" %conf_file% 1>nul 2>&1

			sed -i "s/@@BIZ_ID@@/%biz_id%/g" %relese_conf_file% 1>nul 2>&1
			sed -i "s/@@CLOUD_ID@@/%cloud_id%/g" %relese_conf_file% 1>nul 2>&1
			sed -i "s/@@AGENT_LAN_IP@@/%conn_ip%/g" %relese_conf_file% 1>nul 2>&1
			sed -i "s/@@EXTERNAL_IP@@/%data_ip%/g" %relese_conf_file% 1>nul 2>&1

			rem 替换agent.conf的@@PROXY_IP@@
			for /f "tokens=1,2 delims=-" %%i in ("%proxy_in_ip%") do (
				if not "%%j" == "" (
					sed -i "s/@@PROXY_IP0@@/%%i/g" %relese_conf_file% 1>nul 2>&1
					sed -i "s/@@PROXY_IP1@@/%%j/g" %relese_conf_file% 1>nul 2>&1
				) else (
					sed -i "/@@PROXY_IP1@@/d" %relese_conf_file% 1>nul 2>&1
					sed -i "/@@PROXY_IP0@@/s/,//2" %relese_conf_file% 1>nul 2>&1
					sed -i "s/@@PROXY_IP0@@/%%i/g" %relese_conf_file% 1>nul 2>&1
				)
			)

			rem 替换iagent.conf的@@PROXY_IP@@
			for /f "tokens=1,2 delims=-" %%i in ("%proxy_in_ip%") do (
				if not "%%j" == "" (
					sed -i "s/@@PROXY_IP0@@/%%i/g" %conf_file% 1>nul 2>&1
					sed -i "s/@@PROXY_IP1@@/%%j/g" %conf_file% 1>nul 2>&1
				) else (
					sed -i "/@@PROXY_IP1@@/d" %conf_file% 1>nul 2>&1
					sed -i "/@@PROXY_IP0@@/s/,//2" %conf_file% 1>nul 2>&1
					sed -i "s/@@PROXY_IP0@@/%%i/g" %conf_file% 1>nul 2>&1
				)
			)

			rem 判断@@AGENT_LAN_IP@@是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@AGENT_LAN_IP@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@AGENT_LAN_IP@@ failed ID/install gseagent
					goto :EOF
				)
			)

			rem 判断@@EXTERNAL_IP@@是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@EXTERNAL_IP@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@EXTERNAL_IP@@ failed ID/install gseagent
					goto :EOF
				)
			)

			rem 判断PROXY_IP是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@PROXY_IP@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@PROXY_IP@@ failed ID/install gseagent
					goto :EOF
				)
			)

			rem 判断CLOUD_ID是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@CLOUD_ID@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@CLOUD_ID@@ failed ID/install gseagent
					goto :EOF
				)
			)

			rem 判断@@BIZ_ID@@是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@BIZ_ID@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@BIZ_ID@@ failed ID/install gseagent
					goto :EOF
				)
			)

		) else (
			sed -i "s/@@AGENT_LAN_IP@@/%conn_ip%/g" %relese_conf_file% 1>nul 2>&1
			sed -i "s/@@EXTERNAL_IP@@/%data_ip%/g" %relese_conf_file% 1>nul 2>&1

			rem 判断@@AGENT_LAN_IP@@是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@AGENT_LAN_IP@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@AGENT_LAN_IP@@ failed ID/install gseagent
					goto :EOF
				)
			)

			rem 判断@@EXTERNAL_IP@@是否替换成功
			for /f "delims=" %%i in ('type %relese_conf_file%^|findstr "@@EXTERNAL_IP@@"') do (
				if not "%%i" == "" (
					echo [%local_ip%] %cu_date% %cu_time% setup failed -- Replace the @@EXTERNAL_IP@@ failed ID/install gseagent
					goto :EOF
				)
			)
		)
	)

    rem 删除sed临时文件
    dir/b "%cd%"|findstr /i /r "sed[^\.].*">tmp.txt
    for /f "usebackq" %%i in (tmp.txt) do del /q /f %%i
    del /q /f tmp.txt

    rem 复制gsecmdline到 PATH 路径下
    copy %gse_install_path%\plugins\bin\gsecmdline.exe C:\Windows\System32\ >>error.log 1>nul 2>&1

	rem 启动进程
	cd /d %gse_install_path%\agent\bin
	if not exist %cd:~0,-9%.service_id (set _service_id=) else (set /p service_id=<%cd:~0,-9%.service_id && set _service_id=_%service_id%)
	gse_agent_daemon.exe --file %gse_install_path%\agent\etc\agent.conf --name gse_agent_daemon%_service_id% 1>nul 2>&1
    ping -n 4 127.0.0.1 1>nul 2>&1
	wmic process where name='gse_agent_daemon.exe' get processid,executablepath,name 2>&1 | findstr /i ^"%gse_install_path%^" 1>nul 2>&1
	if !errorlevel! neq 0 (
		echo [%local_ip%] %cu_date% %cu_time% setup failed -- Process gse_agent_daemon.exe start fail/install gseagent
		goto :EOF
	)
	wmic process where name='gse_agent.exe' get processid,executablepath,name 2>&1 | findstr /i ^"%gse_install_path%^" 1>nul 2>&1
	if !errorlevel! neq 0 (
		echo [%local_ip%] %cu_date% %cu_time% setup failed -- Process gse_agent.exe start fail/install gseagent
		goto :EOF
	)
    echo [%local_ip%] %cu_date% %cu_time% setup done -- setup done/install gseagent
	)
    goto :EOF
)
goto :EOF

:remove_gse_install_path
    set install_dir=%~dp0
    cd /d %install_dir%
	del /Q /S /F %gse_install_path% >>error.log 1>nul 2>&1
	rd /Q /S %gse_install_path% >>error.log 1>nul 2>&1
	rm -rf %gse_install_path% >>error.log 1>nul 2>&1
	del /Q /S /F C:\gse >>error.log 1>nul 2>&1
	rd /Q /S C:\gse >>error.log 1>nul 2>&1
	rm -rf C:\gse >>error.log 1>nul 2>&1
goto :EOF

:help
    echo usage: gse_install.bat
	echo install agent : gse_install.bat -o local_ip -i cloud_id -w proxy_out_ip -l proxy_in_ip -I biz_id -D data_ip -E conn_ip -p gse_install_path -s service_id
	echo  remove agent : gse_install.bat -o local_ip -i cloud_id -w proxy_out_ip -l proxy_in_ip -I biz_id -D data_ip -E conn_ip -p gse_install_path -s service_id -r
    echo OPTIONS
    echo   -o  local ip
    echo   -i  cloud id
    echo   -w  proxy out ip
    echo   -l  proxy in ip
    echo   -I  biz id
    echo   -D  data ip
    echo   -E  conn ip
    echo   -p  gse install path
    echo   -s  gse agent service id
    echo   -r  remove gse agent
goto :EOF

:EOF