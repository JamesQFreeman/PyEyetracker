#include <Windows.h>
#include <Python.h>
#include <tobii/tobii.h>
#include <tobii/tobii_streams.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <ctime>
#include <fstream>
#include <iostream>
#include <string>
#include <chrono>
#include <queue>
#include <sstream>
#include <iomanip>
#include <thread>
#include <mutex>

struct Point
{
	float x, y;
};

std::mutex bufferMutex;
std::queue<Point> buffer;

PyObject* getBuffer() 
{
	auto bufferSize = buffer.size();
	std::cout << "Reading:" << bufferSize << std::endl;
	auto result = PyTuple_New(bufferSize);
	bufferMutex.lock();
	for (unsigned i = 0; i < bufferSize; i++) 
	{
		auto PyPoint = PyTuple_New(2);
		PyTuple_SetItem(PyPoint, 0, PyFloat_FromDouble(buffer.front().x));
		PyTuple_SetItem(PyPoint, 1, PyFloat_FromDouble(buffer.front().y));
		buffer.pop();
		PyTuple_SetItem(result, i, PyPoint);
	}
	bufferMutex.unlock();
	return result;
}

std::string getUnixTimeStampMilli() 
{
	auto current_milli = std::chrono::duration_cast<std::chrono::milliseconds>(
		std::chrono::system_clock::now().time_since_epoch()
		).count();
	return std::to_string(current_milli);
}

void writeBuffer(tobii_gaze_point_t const* gaze_point, void* user_data)
{
	if (gaze_point->validity == TOBII_VALIDITY_VALID)
	{
		Point p;
		p.x = gaze_point->position_xy[0];
		p.y = gaze_point->position_xy[1];
		bufferMutex.lock();
		buffer.push(p);
		bufferMutex.unlock();
	}
}

static void url_receiver(char const* url, void* user_data)
{
	char* buffer = (char*)user_data;
	if (*buffer != '\0') return; // only keep first value
	
	if (strlen(url) < 256)
		strcpy_s(buffer, 256, url);
}


void loopWrite()
{
	tobii_api_t* api;
	tobii_error_t error = tobii_api_create(&api, NULL, NULL);
	assert(error == TOBII_ERROR_NO_ERROR);

	char url[256] = { 0 };
	error = tobii_enumerate_local_device_urls(api, url_receiver, url);
	assert(error == TOBII_ERROR_NO_ERROR && *url != '\0');

	tobii_device_t* device;
	error = tobii_device_create(api, url, &device);
	assert(error == TOBII_ERROR_NO_ERROR);

	error = tobii_gaze_point_subscribe(device, writeBuffer, 0);
	assert(error == TOBII_ERROR_NO_ERROR);
	while (true)
	{
		error = tobii_wait_for_callbacks(NULL, 1, &device);
		assert(error == TOBII_ERROR_NO_ERROR || error == TOBII_ERROR_TIMED_OUT);
		error = tobii_device_process_callbacks(device);
		assert(error == TOBII_ERROR_NO_ERROR);
	}
}


void init()
{
	std::thread (&loopWrite).detach();
}

static PyMethodDef TobiiEyeTracker_methods[] = {
	// The first property is the name exposed to Python, fast_tanh, the second is the C++
	// function name that contains the implementation.
	{ "getBuffer", (PyCFunction)getBuffer, METH_NOARGS, nullptr },

	{ "init", (PyCFunction)init, METH_NOARGS, nullptr },

	// Terminate the array with an object containing nulls.
	{ nullptr, nullptr, 0, nullptr }
};

static PyModuleDef TobiiEyeTracker_module = {
	PyModuleDef_HEAD_INIT,
	"TobiiEyeTracker",                        // Module name to use with Python import statements
	"Provides Tobii Eyetracker's Interface",  // Module description
	0,
	TobiiEyeTracker_methods                   // Structure that defines the methods of the module
};

PyMODINIT_FUNC PyInit_TobiiEyeTracker() {
	return PyModule_Create(&TobiiEyeTracker_module);
}

