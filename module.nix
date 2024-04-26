{ config, lib, pkgs, ... }:

with lib; let
  cfg = config.services.aeza-assistant;
  aeza-assistant = pkgs.callPackage ./package.nix { };
in
{
  options.services.aeza-assistant = {
    enable = mkEnableOption "Enable aeza assistant";

    envFile = mkOption {
      type = types.path;
      description = "Path to env secrets";
    };

    datadir = mkOption {
      type = types.path;
      default = "/var/lib/aeza-assistant";
      description = "Data directory";
    };

    package = mkOption {
      type = types.package;
      default = aeza-assistant;
      description = "Aeza assistant package to use";
    };
  };

  config.systemd.services = mkIf cfg.enable {
    aeza-assistant = {
      enable = true;
      description = "Aeza monitoring telegram bot";
      unitConfig = {
        Type = "simple";
      };
      serviceConfig = {
        User = "aeza-assistant";
        Group = "aeza-assistant";
        WorkingDirectory = cfg.datadir;
        ExecStartPre = "${cfg.package}/bin/aeza-assistant migrate";
        ExecStart = "${cfg.package}/bin/aeza-assistant run";
        Restart = "on-failure";
        RestartSec = "1s";
        EnvironmentFile = cfg.envFile;
      };
      wantedBy = [ "multi-user.target" ];
    };
  };

  config.users = mkIf cfg.enable {
    users.aeza-assistant = {
      isSystemUser = true;
      description = "aeza-assistant user";
      home = cfg.datadir;
      createHome = true;
      group = "aeza-assistant";
    };

    groups.aeza-assistant = { };
  };
}
