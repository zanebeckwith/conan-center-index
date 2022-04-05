from conans import CMake, ConanFile, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class LibOQSConan(ConanFile):
    name = "liboqs"
    description = "An open source C library for quantum-safe cryptographic algorithms"
    license = "MIT"
    topics = ("liboqs", "open-quantum-safe", "encryption", "security", "postquantum")
    homepage = "https://openquantumsafe.org"
    url = "https://github.com/open-quantum-safe/liboqs"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dist_build": [True, False],
        "permit_unsupported_arch": [True, False],
        "use_openssl": [True, False],
        "enable_kem_bike": [True, False],
        "enable_kem_kyber": [True, False],
        "enable_kem_frodokem": [True, False],
        "enable_kem_hqc": [True, False],
        "enable_kem_ntru": [True, False],
        "enable_kem_ntruprime": [True, False],
        "enable_kem_saber": [True, False],
        "enable_kem_sidh": [True, False],
        "enable_kem_sike": [True, False],
        "enable_kem_classic_mceliece": [True, False],
        "enable_sig_picnic": [True, False],
        "enable_sig_dilithium": [True, False],
        "enable_sig_falcon": [True, False],
        "enable_sig_rainbow": [True, False],
        "enable_sig_sphincs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dist_build": True,
        "permit_unsupported_arch": False,
        "use_openssl": True,
        "enable_kem_bike": True,
        "enable_kem_kyber": True,
        "enable_kem_frodokem": True,
        "enable_kem_hqc": True,
        "enable_kem_ntru": True,
        "enable_kem_ntruprime": True,
        "enable_kem_saber": True,
        "enable_kem_sidh": True,
        "enable_kem_sike": True,
        "enable_kem_classic_mceliece": True,
        "enable_sig_picnic": True,
        "enable_sig_dilithium": True,
        "enable_sig_falcon": True,
        "enable_sig_rainbow": True,
        "enable_sig_sphincs": True,
    }

    exports_sources = "CMakeLists.txt"

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.use_openssl:
            self.requires("openssl/1.1.1k")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["OQS_BUILD_ONLY_LIB"] = True

        self._cmake.definitions["OQS_DIST_BUILD"] = self.options.dist_build
        self._cmake.definitions[
            "OQS_PERMIT_UNSUPPORTED_ARCHITECTURE"
        ] = self.options.permit_unsupported_arch
        self._cmake.definitions["OQS_USE_OPENSSL"] = self.options.use_openssl
        self._cmake.definitions["OQS_ENABLE_KEM_BIKE"] = self.options.enable_kem_bike
        self._cmake.definitions["OQS_ENABLE_KEM_KYBER"] = self.options.enable_kem_kyber
        self._cmake.definitions["OQS_ENABLE_KEM_FRODOKEM"] = self.options.enable_kem_frodokem
        self._cmake.definitions["OQS_ENABLE_KEM_HQC"] = self.options.enable_kem_hqc
        self._cmake.definitions["OQS_ENABLE_KEM_NTRU"] = self.options.enable_kem_ntru
        self._cmake.definitions["OQS_ENABLE_KEM_NTRUPRIME"] = self.options.enable_kem_ntruprime
        self._cmake.definitions["OQS_ENABLE_KEM_SABER"] = self.options.enable_kem_saber
        self._cmake.definitions["OQS_ENABLE_KEM_SIDH"] = self.options.enable_kem_sidh
        self._cmake.definitions["OQS_ENABLE_KEM_SIKE"] = self.options.enable_kem_sike
        self._cmake.definitions["OQS_ENABLE_KEM_CLASSIC_MCELIECE"] = self.options.enable_kem_classic_mceliece
        self._cmake.definitions["OQS_ENABLE_SIG_PICNIC"] = self.options.enable_sig_picnic
        self._cmake.definitions["OQS_ENABLE_SIG_DILITHIUM"] = self.options.enable_sig_dilithium
        self._cmake.definitions["OQS_ENABLE_SIG_FALCON"] = self.options.enable_sig_falcon
        self._cmake.definitions["OQS_ENABLE_SIG_RAINBOW"] = self.options.enable_sig_rainbow
        self._cmake.definitions["OQS_ENABLE_SIG_SPHINCS"] = self.options.enable_sig_sphincs

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"liboqs-shared" if self.options.shared else "liboqs-static": "liboqs::liboqs"},
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join(
            "lib", "cmake", "conan-official-{}-targets.cmake".format(self.name)
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "liboqs")
        self.cpp_info.set_property(
            "cmake_target_name",
            "liboqs-shared" if self.options.shared else "liboqs-static",
        )
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.system_libs = ["m"]

        if self.options.use_openssl:
            self.cpp_info.requires = ["openssl::openssl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [
            self._module_file_rel_path
        ]
