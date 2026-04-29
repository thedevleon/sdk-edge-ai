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
0x01000164,0xfffe80f9,0x00001fb9,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0x0000a4ce,0x00001d33,
0x01000164,0x0001de5a,0x00002254,
0x01000164,0xfffee184,0x00001697,
0x01000164,0xffffff6a,0x000027b9,
0x01000164,0xfffef967,0x00001e76,
0x01000164,0xffff8d8e,0x00002469,
0x01000164,0x00012885,0x00003c70,
0x01000164,0x0001b078,0x00001d5b,
0x01000164,0x00014ac3,0x0000286a,
0x01000164,0xfffffee2,0x00003091,
0x01000164,0x000281ef,0x00001506,
0x01000164,0xfffe8dfe,0x00001f9d,
0x01000164,0x0000667c,0x00003054,
0x01000164,0x0002211e,0x00002017,
0x01000164,0xffff6bc1,0x00001958,
0x01000164,0xfffe1ef2,0x00003458,
0x01000164,0xfffec8d6,0x000019f2,
0x01000164,0x000211d3,0x00001638,
0x01000164,0xffff5f8f,0x00001936,
0x01000164,0xfffe8cb8,0x00002cc7,
0x01000164,0x00017f0a,0x00001d1a,
0x01000164,0x00012b30,0x00001b28,
0x01000164,0x0000330d,0x00001e70,
0x01000164,0x000121c2,0x00001f0f,
0x01000164,0x0000f7a5,0x0000517a,
0x01000164,0x00005262,0x00002125,
0x01000164,0xffff2f49,0x00001847,
0x01000164,0x0002d3d8,0x000027de,
0x01000164,0x00015832,0x00002225,
0x01000164,0x000206c3,0x00001828,
0x01000164,0xfffeface,0x00004cb5,
0x01000164,0x0001d12c,0x00003732,
0x01000164,0x00005a9c,0x0000202a,
0x01000164,0x0000827e,0x000022d0,
0x01000164,0xfffeab2d,0x000029ab,
0x01000164,0x0000df3c,0x0000220d,
0x01000164,0x000002a7,0x0000319c,
0x01000164,0x00002146,0x0000124c,
0x01000164,0x0001b0e2,0x000028a3,
0x01000164,0x0000f724,0x00002a7c,
0x01000164,0xfffffd07,0x00002e18,
0x01000164,0x000157c5,0x00003152,
0x01000164,0xffffce0f,0x00002553,
0x01000164,0x00012417,0x00001ce2,
0x01000164,0xfffede05,0x00001c16,
0x01000164,0x00009d58,0x00002afe,
0x01000164,0xffff8cdb,0x00001d78,
0x01000164,0x00011a99,0x00003412,
0x01000164,0xfffeaebc,0x00001e75,
0x01000164,0xffffc6e2,0x00003118,
0x01000164,0x00009b1e,0x000017a5,
0x01000164,0xffff79d5,0x00001ea1,
0x01000164,0x000038be,0x00001c37,
0x01000164,0xffffba86,0x000022d6,
0x01000164,0x000193b6,0x000020a9,
0x01000164,0x000166b5,0x000022d3,
0x01000164,0xfffe3a21,0x00002067,
0x01000164,0xffffff60,0x00003b29,
0x01000164,0x00018dad,0x000023e5,
0x01000164,0x0001e58a,0x00003eac,
0x01000164,0xfffedc0f,0x00001ec2,
0x01000164,0x0000abb7,0x00002563,
0x01000164,0x0001ab57,0x0000284f,
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
        .quant_mult = 103280891,
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
    .output_dequant_round = 19,
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
0x01000164,0x0001b8d0,0x00006c28,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0xfffef79b,0x00009cc7,
0x01000164,0x00023c5f,0x00005d57,
0x01000164,0xffffabf4,0x0000ad1f,
0x01000164,0xfffe2606,0x0000ecaf,
0x01000164,0x0000bc17,0x00008fde,
0x01000164,0x0000d155,0x0000cc4d,
0x01000164,0xffff5410,0x0000e3c1,
0x01000164,0x0002299d,0x00008861,
0x01000164,0xfffdfc9a,0x00019590,
0x01000164,0xffff48c4,0x0000f167,
0x01000164,0x0000d856,0x000065b9,
0x01000164,0x00010caf,0x00006c09,
0x01000164,0xfffe89ef,0x00006eb5,
0x01000164,0xfffed803,0x000168bc,
0x01000164,0x0001bd94,0x0000c125,
0x01000164,0xfffde9c4,0x0000d9d0,
0x01000164,0x00014333,0x00008886,
0x01000164,0xffffe724,0x00008995,
0x01000164,0xffffee33,0x00009ef6,
0x01000164,0x00021119,0x00005cf5,
0x01000164,0xffff9b70,0x00008b32,
0x01000164,0x0000c327,0x0000604d,
0x01000164,0x00008d5c,0x0000be6d,
0x01000164,0xffff5a1a,0x00007d58,
0x01000164,0xffffc9af,0x0000bc49,
0x01000164,0x000275ca,0x0000473f,
0x01000164,0x00012699,0x00008c62,
0x01000164,0xffff9b39,0x00009078,
0x01000164,0xffff74ab,0x00004521,
0x01000164,0xfffe5879,0x0000f451,
0x01000164,0xfffef6af,0x00015616,
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
    .output_dequant_round = 19,
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
0x030000c8,0x00010000,0x00000000,0x03010000,0x00010b05,
0x01000180,0x00000002,0x80000000,
0x000001a4,0x00000000,
0x000001cc,0x00000000,
0x01000164,0xffffeee4,0x0009516b,
0x000000d8,0x01000005,
0x000000f0,0x00000100,
0x01000164,0xfffff529,0x0009f049,
0x01000164,0x00007a26,0x00076317,
0x01000164,0xffff39d9,0x000a7dec,
0x01000164,0x0000034a,0x000b692d,
0x01000164,0xffff6a8b,0x0008b327,
0x01000164,0xffff3e74,0x0006f9cc,
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
    .output_dequant_round = 19,
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
