{
  description = "Aeza monitoring telegram bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      all = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          aeza-assistant = pkgs.callPackage ./package.nix { };
        in {
          packages = {
            inherit aeza-assistant;
            default = aeza-assistant;
          };

          devShells.default = pkgs.mkShell {
            inputsFrom = [ aeza-assistant ];
            packages = [ pkgs.poetry ];
          };
        });
    in {
      nixosModules.aeza-assistant = import ./module.nix;
      nixosModules.default = self.nixosModules.aeza-assistant;

      overlays.aeza-assistant = (final: prev: { aeza-assistant = all.packages.${prev.system}.aeza-assistant; });
      overlays.default = self.overlays.aeza-assistant;
    } // all;
}
