@echo off
echo @@@ IME�\�����͗���\�� @@@  2020/6/4��
echo +++

rem ��ƃf�B���N�g�ύX
%~d0
cd /d %~dp0

rem �擾�f�[�^�ۑ���쐬
set time_tmp=%time: =0%
set now=%date:/=%%time_tmp:~0,2%%time_tmp:~3,2%%time_tmp:~6,2%
rem echo %now%
set BUFolder=%now%
mkdir %BUFolder%


rem IME�\�����̓f�[�^�擾
mkdir %BUFolder%\JpnIHDS
set JpnIHDS_dat=%APPDATA%\Microsoft\InputMethod\Shared\JpnIHDS.dat
IF exist %JpnIHDS_dat% goto NEXT_Process
echo "Error : JpnIHDS.dat not found"
pause
exit /b

:NEXT_Process
copy %JpnIHDS_dat% %BUFolder%\JpnIHDS\
echo JpnIHDS.dat�� %BUFolder%\JpnIHDS\�t�H���_�ɕۑ����܂���

rem JpnIHDS.dat����IME�\�����͗����𒊏o
echo ���͊J�n�D�D�D
IME_jp_parse.exe .\%BUFolder%\JpnIHDS\JpnIHDS.dat .\%BUFolder%\IME_JpnIHDS_history.csv.tmp
sort %BUFolder%\IME_JpnIHDS_history.csv.tmp > %BUFolder%\IME_JpnIHDS_history.csv
del %BUFolder%\IME_JpnIHDS_history.csv.tmp

echo +++
echo +++ ����!!
echo +++ ���ʂ� %BUFolder%\IME_JpnIHDS_history.csv �ɕۑ�����܂���
echo +++ �y���Ӂz�����̎����́APC�ɐݒ肳�ꂽ�n��̃��[�J���^�C���iJST���j�ł��I�I
echo +++
echo +++ �����ď�L�t�@�C�����������ŕ\�����܂�
echo +++ �y���Ӂz�f�[�^���ɔ��p�́u"�v�i�R�[�e�[�V�����j���܂܂�Ă���Ƃ��A
echo +++ csv�t�@�C����Excel�ŊJ���ƕ\�������������Ȃ�ꍇ������܂��I
echo +++
echo +++   Please push any key...
pause > nul

rem ���ʕ\��
notepad %BUFolder%\IME_JpnIHDS_history.csv
