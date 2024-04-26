{ lib
, python3
, python3Packages
}:

python3.pkgs.buildPythonPackage rec {
  pname = "aeza-assistant";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = with python3Packages; [
    poetry-core
  ];

  preBuild = ''sed -i "s@script_location = migrations@script_location = $out/${python3.sitePackages}/aeza_assistant/migrations@g" ./aeza_assistant/alembic.ini'';

  propagatedBuildInputs = with python3Packages; [
    aiogram
    aiohttp
    sqlalchemy
    asyncpg
    alembic
    python-dateutil
  ];
}