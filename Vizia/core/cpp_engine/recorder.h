// Vizia/core/cpp_engine/recorder.h

#ifndef RECORDER_H
#define RECORDER_H

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

extern "C" {
    EXPORT void start_capture(const char* output_path, int fps);
    EXPORT void stop_capture();
    EXPORT void pause_capture(bool pause);
}

#endif // RECORDER_H