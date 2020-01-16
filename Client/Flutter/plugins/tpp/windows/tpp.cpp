// Copyright 2019 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include "tpp.h"

#include <windows.h>

#include <VersionHelpers.h>
#include <flutter/method_channel.h>
#include <flutter/plugin_registrar.h>
#include <flutter/standard_method_codec.h>
#include <memory>
#include <sstream>

#include <string>

using namespace std;

namespace {

    using flutter::EncodableMap;
    using flutter::EncodableValue;


    class TppPlugin : public flutter::Plugin {
    public:
        static void RegisterWithRegistrar(flutter::PluginRegistrar *registrar);

        virtual ~TppPlugin();

    private:
        TppPlugin();

        // Called when a method is called on plugin channel;
        void HandleMethodCall(
                const flutter::MethodCall <EncodableValue> &method_call,
                std::unique_ptr <flutter::MethodResult<EncodableValue>> result);
    };

// static
    void TppPlugin::RegisterWithRegistrar(
            flutter::PluginRegistrar *registrar) {
        auto channel = std::make_unique < flutter::MethodChannel < EncodableValue >> (
                registrar->messenger(), "tpp",
                        &flutter::StandardMethodCodec::GetInstance());

        // Uses new instead of make_unique due to private constructor.
        std::unique_ptr <TppPlugin> plugin(new TppPlugin());

        channel->SetMethodCallHandler(
                [plugin_pointer = plugin.get()](const auto &call, auto result) {
                    plugin_pointer->HandleMethodCall(call, std::move(result));
                });

        registrar->AddPlugin(std::move(plugin));
    }

    TppPlugin::TppPlugin() = default;

    TppPlugin::~TppPlugin() = default;

    void TppPlugin::HandleMethodCall(
        const flutter::MethodCall<flutter::EncodableValue> &method_call,
        std::unique_ptr<flutter::MethodResult<flutter::EncodableValue>> result) {

        //faverolles
        if (method_call.method_name().compare("getCurrentDirectory") == 0) {
            std::ostringstream version_stream;
//            const int asdf = 260;
//            wchar_t result[ asdf ];
//            GetModuleFileName( NULL, result, asdf );

//            int i = 0;
//            do{
//                version_stream << (char)result[i];
//            }while(result[i] != '\0');
//            version_stream << result << " ";
            version_stream << "Not Implemented";
            flutter::EncodableValue response(version_stream.str());
//            std::ostringstream version_stream;
//            version_stream << "asdfasdfasdfasdf";
//            flutter::EncodableValue response(version_stream.str());
            result->Success(&response);
        } else {
            result->NotImplemented();
        }
    }

}  // namespace

void TppPluginRegisterWithRegistrar(
        FlutterDesktopPluginRegistrarRef registrar) {
    // The plugin registrar owns the plugin, registered callbacks, etc., so must
    // remain valid for the life of the application.
    static auto *plugin_registrar = new flutter::PluginRegistrar(registrar);
    TppPlugin::RegisterWithRegistrar(plugin_registrar);
}
