// C shim between Python (ctypes) and the Lean-compiled `run` at type Float.
#include <lean/lean.h>
#include <string.h>

// Provided by the Lean runtime but not declared in lean.h.
extern void lean_initialize_runtime_module(void);
extern void lean_initialize_thread(void);

extern lean_object *initialize_heat_HeatFFI(uint8_t builtin, lean_object *w);
extern lean_object *heat_run_float_array(double r, size_t steps, lean_object *xs);

static int lean_ready = 0;
static _Thread_local int thread_ready = 0;

// Initialise the Lean runtime and modules. Returns 0 on success.
int heat_init(void) {
  if (lean_ready) return 0;
  lean_initialize_runtime_module();
  lean_set_panic_messages(false);
  lean_object *res = initialize_heat_HeatFFI(1, lean_io_mk_world());
  lean_set_panic_messages(true);
  if (!lean_io_result_is_ok(res)) {
    lean_io_result_show_error(res);
    lean_dec_ref(res);
    return -1;
  }
  lean_dec_ref(res);
  lean_io_mark_end_initialization();
  lean_ready = 1;
  thread_ready = 1;
  return 0;
}

// Run `steps` FTCS steps with coefficient `r` on `in[0..n)`, writing to `out`.
// `in` and `out` may alias. Returns 0 on success.
int heat_run(double r, size_t steps, const double *in, double *out, size_t n) {
  if (!lean_ready) return -1;
  if (!thread_ready) {  // calls from a thread Lean has not seen yet
    lean_initialize_thread();
    thread_ready = 1;
  }
  lean_object *xs = lean_alloc_sarray(sizeof(double), n, n);
  memcpy(lean_float_array_cptr(xs), in, n * sizeof(double));
  lean_object *ys = heat_run_float_array(r, steps, xs);  // consumes xs
  if (lean_sarray_size(ys) != n) { lean_dec(ys); return -2; }
  memcpy(out, lean_float_array_cptr(ys), n * sizeof(double));
  lean_dec(ys);
  return 0;
}
