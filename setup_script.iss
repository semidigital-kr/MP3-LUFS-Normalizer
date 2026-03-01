[Setup]
; 프로그램 기본 정보
AppName=MP3 LUFS Normalizer
AppVersion=0.0.1
AppPublisher=SEMIDIGITAL
AppPublisherURL=https://semidigital.co.kr
; 기본 설치 경로 (C:\Program Files (x86)\SEMIDIGITAL\MP3 LUFS Normalizer)
DefaultDirName={autopf}\SEMIDIGITAL\MP3 LUFS Normalizer
DefaultGroupName=SEMIDIGITAL
; 만들어질 설치 파일의 이름
OutputBaseFilename=MP3_LUFS_Normalizer_Setup_v0.0.1
; 설치 파일 아이콘 (방금 변환한 ico 파일 적용)
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
; 설치 후 컴퓨터 재시작 묻지 않음
DisableProgramGroupPage=yes

[Files]
; 설치될 파일들 목록 (현재 스크립트 파일이 있는 폴더 기준)
Source: "main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "sd.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "PretendardVariable.ttf"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; social 폴더 안의 내용물 전체 복사
Source: "social\*"; DestDir: "{app}\social"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 바탕화면 및 시작 메뉴에 바로가기 아이콘 생성
Name: "{group}\MP3 LUFS Normalizer"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\MP3 LUFS Normalizer"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"