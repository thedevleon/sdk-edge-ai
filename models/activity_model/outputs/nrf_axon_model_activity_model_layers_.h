/*********************************************************************************
 * Auto-generated nrf Axon compiled neural network model header file.
 * Model Name: activity_model
 * Axon Neural Network Compiler Version: 1.2.0
 *********************************************************************************/
#ifdef __cplusplus
extern "C" {
#endif
#if (AXON_LAYER_TEST_START_LAYER<=0) && (AXON_LAYER_TEST_STOP_LAYER>=0)

const NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE cmd_buffer_activity_model_0_0[253] = {
// segment 0,length 252,Axon NN
0x1fff00fc,
0x09000080,0x00010096,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)nrf_axon_interlayer_buffer,0x00330096,0x00040000,0x00010096,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)axon_model_const_activity_model.l00_weights,0x00330040,0x00000096,0x00000000,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)NULL,
0x040000ac,0x00010001,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)((uint8_t*)(nrf_axon_interlayer_buffer)+0x98),0x00050004,0x00000004,0x00000000,
0x030000c8,0x00010000,0x00000000,0x03010000,0x00011703,
0x01000180,0x00000003,0x00000000,
0x000001a4,0x00000000,
0x010001c8,0xc0000000,0xc0000000,
0x01000164,0x0000042d,0x000075ab,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0x00000438,0x00005b61,
0x01000164,0xffffb272,0x00006bc9,
0x01000164,0xfffeeae1,0x0000df0e,
0x01000164,0xffffebf1,0x00006af2,
0x01000164,0xfffff764,0x00008501,
0x01000164,0xffff154d,0x000091fe,
0x01000164,0xffffd694,0x00008aaf,
0x01000164,0xffffbcef,0x00007741,
0x01000164,0xffffa40f,0x000088a8,
0x01000164,0xffffff20,0x00008caa,
0x01000164,0xffffb8d4,0x00007063,
0x01000164,0x00005652,0x00006ccf,
0x01000164,0xffff29e0,0x00004195,
0x01000164,0x000031c1,0x00007614,
0x01000164,0xffffae7f,0x0000af14,
0x01000164,0xffff8396,0x000083e7,
0x01000164,0x00014872,0x0000ad59,
0x01000164,0xfffffeec,0x00005e0a,
0x01000164,0xffff78a9,0x00005d6b,
0x01000164,0xffffd9b0,0x000076ff,
0x01000164,0xffffed12,0x00006f32,
0x01000164,0xffffef84,0x000071bc,
0x01000164,0x00002b4f,0x00005c18,
0x01000164,0xfffff5ab,0x000074aa,
0x01000164,0x0000a136,0x00007d10,
0x01000164,0xffff38de,0x00006da6,
0x01000164,0x00003cd8,0x00005d18,
0x01000164,0x0000e78c,0x000053ee,
0x01000164,0xfffff791,0x000078f1,
0x01000164,0xffffc0b7,0x0000a86b,
0x01000164,0xfffff06d,0x00006703,
0x01000164,0x0000247e,0x00007dba,
0x01000164,0xfffff929,0x00007670,
0x01000164,0x000099c8,0x00005876,
0x01000164,0xffffe366,0x00007852,
0x01000164,0xffff74b3,0x00008a84,
0x01000164,0x00006b64,0x00007c7d,
0x01000164,0x0000c227,0x00006d79,
0x01000164,0x00000b9b,0x000066ea,
0x01000164,0xffff5f4c,0x00007887,
0x01000164,0xffff9a62,0x0000784e,
0x01000164,0xffffbe9a,0x00006ca6,
0x01000164,0xffffe4fa,0x00006f6f,
0x01000164,0xffffe080,0x000080c8,
0x01000164,0xffffa276,0x00007525,
0x01000164,0xffff70b3,0x00006987,
0x01000164,0x00013c26,0x0000b196,
0x01000164,0xfffe0525,0x00006adb,
0x01000164,0xffff5062,0x0000728f,
0x01000164,0xfffff58b,0x000071e2,
0x01000164,0x00004d72,0x00006625,
0x01000164,0x000053fb,0x00006011,
0x01000164,0xfffff004,0x00007af4,
0x01000164,0xfffffb58,0x0000677c,
0x01000164,0x00000c11,0x000050d1,
0x01000164,0xffffd7a2,0x000082bf,
0x01000164,0xffffa629,0x0000b241,
0x01000164,0xffffcefc,0x000077d6,
0x01000164,0x00008dac,0x00006ab7,
0x01000164,0x00008b97,0x00006fb7,
0x01000164,0xffffa0f8,0x0000652a,
0x01000164,0xffffae94,0x000077d1,
0x01000164,0xffffec5e,0x00007b8e,
0x07000080,0x00010100,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)((uint8_t*)(nrf_axon_interlayer_buffer)+0x98),0x01830400,0x00000000,0x00010004,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)axonpro_int8_packing_filter,0x00330001,0x00000004,
0x040000a8,0x00150000,0x00010040,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)nrf_axon_interlayer_buffer,0x00030040,0x00000040,
0x000000c0,0x00000000,
0x030000c8,0x00000000,0x01040000,0x00000000,0x00000003,
0x000000d8,0x00000001,
0x000000f0,0x00000100,
};
const nrf_axon_nn_compiled_model_layer_s model_activity_model_0_0 = {
  .base = {
    .compiler_version = 0x00010200,
    .model_name = "activity_model",
    .labels = labels_activity_model,
    .inputs = {
      {// 0
        .ptr = (int8_t*)nrf_axon_interlayer_buffer,
        .dimensions = {
          .height = 1,
          .width = 150,
          .channel_cnt = 1,
          .byte_width = 1,
        },
        .quant_mult = 654671,
        .stride = 150,
        .quant_round = 19,
        .quant_zp = -27,
        .is_external = true,
      }, // 0
    }, // inputs
    .input_cnt = 1,
    .external_input_ndx = 0,
    .output_ptr = (int8_t*)nrf_axon_interlayer_buffer,
    .packed_output_buf = NULL,

    .interlayer_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_IL_BUFFER_USED,
    .psum_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_PSUM_BUFFER_USED,
    .cmd_buffer_ptr = cmd_buffer_activity_model_0_0,

    .model_const_ptr = &axon_model_const_activity_model,
    .model_const_size = sizeof(axon_model_const_activity_model),
    .cmd_buffer_len = 253,
    .persistent_vars = {
      .count = 0,
    },

    .output_dimensions = {
      .height = 1,
      .width = 64,
      .channel_cnt = 1,
      .byte_width = 1,
    },
    .output_dequant_mult = 1,
    .output_dequant_round = 17,
    .output_dequant_zp = 0,
    .output_stride = 64,
    .is_layer_model = true,
    .extra_output_cnt = 0,
    .extra_outputs = NULL,
  },// .base
  .layer_ndx = 0,
  .input0_layer_ndx = -1,
  .input1_layer_ndx = -1,
};
#endif
#if (AXON_LAYER_TEST_START_LAYER<=1) && (AXON_LAYER_TEST_STOP_LAYER>=1)

const NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE cmd_buffer_activity_model_1_1[157] = {
// segment 0,length 156,Axon NN
0x1fff009c,
0x09000080,0x00010040,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)nrf_axon_interlayer_buffer,0x00330040,0x00040000,0x00010040,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)axon_model_const_activity_model.l01_weights,0x00330020,0x00000040,0x00000000,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)NULL,
0x040000ac,0x00010001,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)((uint8_t*)(nrf_axon_interlayer_buffer)+0x40),0x00050004,0x00000004,0x00000000,
0x030000c8,0x00010000,0x00000000,0x03010000,0x00011703,
0x01000180,0x00000003,0x00000000,
0x000001a4,0x00000000,
0x010001c8,0xc0000000,0xc0000000,
0x01000164,0xfffecc63,0x0000c809,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0xffff07aa,0x000104b0,
0x01000164,0xfffe6eae,0x000105bf,
0x01000164,0xfffdc433,0x0000dbb0,
0x01000164,0x000086ef,0x00007898,
0x01000164,0xffff8382,0x00007b8f,
0x01000164,0xfffd8e07,0x0000a51c,
0x01000164,0xffff34ce,0x0000b957,
0x01000164,0xfffee9f5,0x0000aed6,
0x01000164,0x0000c1cc,0x000094ad,
0x01000164,0xffff0537,0x00010351,
0x01000164,0x00014006,0x00007524,
0x01000164,0xffff60bf,0x0000b7a7,
0x01000164,0xffff8e9e,0x0000a0e7,
0x01000164,0xfffe8fa9,0x00009e61,
0x01000164,0xffffb205,0x00008af2,
0x01000164,0xfffe533a,0x0000b91c,
0x01000164,0x000085e2,0x0000a825,
0x01000164,0xffff7d5d,0x0000e1cf,
0x01000164,0x0000e616,0x0000c5c0,
0x01000164,0xffff27f8,0x0000d738,
0x01000164,0xfffe3e8b,0x000143dd,
0x01000164,0xffff6f4d,0x00019b9d,
0x01000164,0xffff4e77,0x00009b0b,
0x01000164,0xfffeb0b9,0x0000bb7f,
0x01000164,0xfffee495,0x0000f2b6,
0x01000164,0xfffdf986,0x0000a68e,
0x01000164,0xfffe965d,0x00010824,
0x01000164,0xffffe972,0x00015687,
0x01000164,0xffff47fe,0x00007a07,
0x01000164,0xfffecfad,0x0000cc5f,
0x01000164,0xffff89f4,0x0000c814,
0x07000080,0x00010080,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)((uint8_t*)(nrf_axon_interlayer_buffer)+0x40),0x03030400,0x00000000,0x00010004,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)axonpro_int8_packing_filter,0x00330001,0x00000004,
0x040000a8,0x00150000,0x00010020,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)nrf_axon_interlayer_buffer,0x00030020,0x00000020,
0x000000c0,0x00000000,
0x030000c8,0x00000000,0x01040000,0x00000000,0x00000003,
0x000000d8,0x00000001,
0x000000f0,0x00000100,
};
const nrf_axon_nn_compiled_model_layer_s model_activity_model_1_1 = {
  .base = {
    .compiler_version = 0x00010200,
    .model_name = "activity_model",
    .labels = labels_activity_model,
    .inputs = {
      {// 0
        .ptr = (int8_t*)nrf_axon_interlayer_buffer,
        .dimensions = {
          .height = 1,
          .width = 64,
          .channel_cnt = 1,
          .byte_width = 1,
        },
        .stride = 64,
        .is_external = false,
      }, // 0
    }, // inputs
    .input_cnt = 1,
    .external_input_ndx = -1,
    .output_ptr = (int8_t*)nrf_axon_interlayer_buffer,
    .packed_output_buf = NULL,

    .interlayer_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_IL_BUFFER_USED,
    .psum_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_PSUM_BUFFER_USED,
    .cmd_buffer_ptr = cmd_buffer_activity_model_1_1,

    .model_const_ptr = &axon_model_const_activity_model,
    .model_const_size = sizeof(axon_model_const_activity_model),
    .cmd_buffer_len = 157,
    .persistent_vars = {
      .count = 0,
    },

    .output_dimensions = {
      .height = 1,
      .width = 32,
      .channel_cnt = 1,
      .byte_width = 1,
    },
    .output_dequant_mult = 1,
    .output_dequant_round = 17,
    .output_dequant_zp = 0,
    .output_stride = 32,
    .is_layer_model = true,
    .extra_output_cnt = 0,
    .extra_outputs = NULL,
  },// .base
  .layer_ndx = 1,
  .input0_layer_ndx = 0,
  .input1_layer_ndx = -1,
};
#endif
#if (AXON_LAYER_TEST_START_LAYER<=2) && (AXON_LAYER_TEST_STOP_LAYER>=2)

const NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE cmd_buffer_activity_model_2_2[55] = {
// segment 0,length 54,Axon NN
0x1fff0036,
0x09000080,0x00010020,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)nrf_axon_interlayer_buffer,0x00330020,0x00040000,0x00010020,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)axon_model_const_activity_model.l02_weights,0x00330007,0x00000020,0x00000000,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)NULL,
0x040000ac,0x00010001,(NRF_AXON_PLATFORM_BITWIDTH_UNSIGNED_TYPE)((uint8_t*)(nrf_axon_interlayer_buffer)+0x3c),0x00050004,0x00000004,0x00000000,
0x030000c8,0x00010000,0x00000000,0x03010000,0x00010d05,
0x01000180,0x00000002,0x80000000,
0x000001a4,0x00000000,
0x000001cc,0x00000000,
0x01000164,0x000035b3,0x002bbfbc,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0xffffbd8e,0x00373f3b,
0x01000164,0xfffff12b,0x0035405c,
0x01000164,0x00001e25,0x002daaf1,
0x01000164,0x0000bc0a,0x0021314d,
0x01000164,0xffff506b,0x00356725,
0x01000164,0xffff2989,0x0030afa7,
};
const nrf_axon_nn_compiled_model_layer_s model_activity_model_2_2 = {
  .base = {
    .compiler_version = 0x00010200,
    .model_name = "activity_model",
    .labels = labels_activity_model,
    .inputs = {
      {// 0
        .ptr = (int8_t*)nrf_axon_interlayer_buffer,
        .dimensions = {
          .height = 1,
          .width = 32,
          .channel_cnt = 1,
          .byte_width = 1,
        },
        .stride = 32,
        .is_external = false,
      }, // 0
    }, // inputs
    .input_cnt = 1,
    .external_input_ndx = -1,
    .output_ptr = (int8_t*)((uint8_t*)(nrf_axon_interlayer_buffer)+0x3c),
    .packed_output_buf = NULL,

    .interlayer_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_IL_BUFFER_USED,
    .psum_buffer_needed = NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_PSUM_BUFFER_USED,
    .cmd_buffer_ptr = cmd_buffer_activity_model_2_2,

    .model_const_ptr = &axon_model_const_activity_model,
    .model_const_size = sizeof(axon_model_const_activity_model),
    .cmd_buffer_len = 55,
    .persistent_vars = {
      .count = 0,
    },

    .output_dimensions = {
      .height = 1,
      .width = 7,
      .channel_cnt = 1,
      .byte_width = 4,
    },
    .output_dequant_mult = 1,
    .output_dequant_round = 17,
    .output_dequant_zp = 0,
    .output_stride = 28,
    .is_layer_model = true,
    .extra_output_cnt = 0,
    .extra_outputs = NULL,
  },// .base
  .layer_ndx = 2,
  .input0_layer_ndx = 1,
  .input1_layer_ndx = -1,
};
#endif
#define MODEL_activity_model_FIRST_COMPUTE_LAYER (0)
nrf_axon_nn_compiled_model_layer_s const *model_activity_model_layer_list[] = {
	#if (AXON_LAYER_TEST_START_LAYER<=0) && (AXON_LAYER_TEST_STOP_LAYER>=0)
  &model_activity_model_0_0,
#else
  NULL,
#endif
#if (AXON_LAYER_TEST_START_LAYER<=1) && (AXON_LAYER_TEST_STOP_LAYER>=1)
  &model_activity_model_1_1,
#else
  NULL,
#endif
#if (AXON_LAYER_TEST_START_LAYER<=2) && (AXON_LAYER_TEST_STOP_LAYER>=2)
  &model_activity_model_2_2,
#else
  NULL,
#endif

};

#ifdef __cplusplus
}
#endif
