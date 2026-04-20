const int8_t activity_model_test_input_vector_0[1][1][150] = {
{{-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-22,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-38,-22,-23,-37,-22,-23,-38,-22,-23,-38,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-22,-37,-22,-23,-37,-22,-23,-37,-22,-23,-37,-22,-22,-37,-22,-22,-38,-22,-23,-38,-22,-22,-37,-22,-22,},},
};
const int32_t activity_model_expected_output_vector_0[1][1][7] = {
{{453589,653682,358275,66127,160387,109796,95035,},},
};
#if !AXON_MINIMUM_TEST_VECTORS
const int8_t activity_model_test_input_vector_1[1][1][150] = {
{{-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-26,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-26,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-26,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,-25,-24,-15,},},
};
const int32_t activity_model_expected_output_vector_1[1][1][7] = {
{{973327,1491227,384688,493942,980907,-435768,86077,},},
};
const int8_t activity_model_test_input_vector_2[1][1][150] = {
{{-40,-22,-14,-40,-23,-15,-40,-24,-17,-40,-25,-19,-41,-25,-20,-42,-23,-19,-42,-22,-19,-42,-21,-18,-41,-21,-17,-40,-21,-16,-40,-21,-15,-40,-23,-15,-39,-24,-16,-39,-25,-16,-39,-25,-16,-39,-23,-16,-39,-21,-15,-39,-20,-15,-39,-19,-15,-38,-19,-15,-37,-20,-15,-37,-20,-15,-38,-21,-15,-38,-21,-15,-38,-20,-15,-38,-20,-16,-38,-19,-17,-38,-19,-17,-39,-19,-18,-39,-18,-19,-40,-18,-19,-41,-19,-19,-42,-19,-20,-42,-20,-20,-41,-20,-21,-41,-20,-21,-40,-20,-21,-39,-20,-22,-40,-19,-23,-41,-19,-24,-41,-19,-24,-41,-19,-24,-40,-19,-25,-39,-20,-25,-37,-21,-25,-37,-21,-26,-38,-21,-26,-39,-21,-27,-39,-20,-27,-40,-20,-27,},},
};
const int32_t activity_model_expected_output_vector_2[1][1][7] = {
{{385691,832241,651797,387628,102233,944163,32717,},},
};
#endif

const int32_t* activity_model_input_test_vectors[] = {
  (int32_t*)activity_model_test_input_vector_0,
#if !AXON_MINIMUM_TEST_VECTORS
  (int32_t*)activity_model_test_input_vector_1,
  (int32_t*)activity_model_test_input_vector_2,
#endif
};
const int32_t* activity_model_expected_output_vectors[] = {
  (int32_t*)activity_model_expected_output_vector_0,
#if !AXON_MINIMUM_TEST_VECTORS
  (int32_t*)activity_model_expected_output_vector_1,
  (int32_t*)activity_model_expected_output_vector_2,
#endif
};

#if AXON_LAYER_TEST_VECTORS
#if (AXON_LAYER_TEST_START_LAYER<=1) && (AXON_LAYER_TEST_STOP_LAYER>=0)
const int8_t activity_model_expected_output_vector_0_layer_0[1][1][64] = {
{{-128,-128,-128,-128,-128,-128,-128,-128,-128,-128,-126,-128,-120,-94,-128,-128,-128,-128,-107,-128,-128,-128,-128,-120,-128,-128,-128,-115,-128,-128,-128,-128,-128,-128,-105,-127,-118,-128,-128,-128,-128,-128,-128,-128,-128,-112,-128,-128,-128,-122,-128,-128,-128,-128,-127,-114,-128,-128,-128,-128,-128,-128,-128,-128,},},
};
#endif
#if (AXON_LAYER_TEST_START_LAYER<=2) && (AXON_LAYER_TEST_STOP_LAYER>=1)
const int8_t activity_model_expected_output_vector_0_layer_1[1][1][32] = {
{{-128,-125,-125,-117,-119,-122,-128,-128,-128,-128,-128,-118,-128,-121,-124,-128,-128,-128,-128,-128,-128,-127,-128,-128,-128,-128,-128,-128,-126,-122,-128,-128,},},
};
#endif
#if (AXON_LAYER_TEST_START_LAYER<=3) && (AXON_LAYER_TEST_STOP_LAYER>=2)
const int32_t activity_model_expected_output_vector_0_layer_2[1][1][7] = {
{{453589,653682,358275,66127,160387,109796,95035,},},
};
#endif
#endif

const int32_t* activity_model_layer_expected_output_vectors[] = {
#if AXON_LAYER_TEST_VECTORS
#if (AXON_LAYER_TEST_START_LAYER<=1) && (AXON_LAYER_TEST_STOP_LAYER>=0)
  (int32_t*)activity_model_expected_output_vector_0_layer_0,
#else
  NULL,
#endif
#if (AXON_LAYER_TEST_START_LAYER<=2) && (AXON_LAYER_TEST_STOP_LAYER>=1)
  (int32_t*)activity_model_expected_output_vector_0_layer_1,
#else
  NULL,
#endif
#if (AXON_LAYER_TEST_START_LAYER<=3) && (AXON_LAYER_TEST_STOP_LAYER>=2)
  (int32_t*)activity_model_expected_output_vector_0_layer_2,
#else
  NULL,
#endif
#else
  NULL,
#endif
};

