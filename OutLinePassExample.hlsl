
        Pass
        {
            Name "Outline"
			Tags { "LightMode" = "OutLine" }
			ZWrite On
			Lighting Off
            Cull Front

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
			
			#pragma shader_feature_local _NORMAL_VERT _NORMAL_VERTEXCOLORSMOOTH

            struct Attributes
			{
				float3 positionOS : POSITION;
				float2 texcoord : TEXCOORD0;
				float3 normalOS : NORMAL;
				float4 tangentOS : TANGENT;
				float4 smoothNormal : TEXCOORD2;
				float4 color : COLOR;
			};

			struct Varyings
			{	
				float4 positionCS : SV_POSITION;
				float2 uv: TEXCOORD1;
				float3 normalVS : TEXCOORD2;
			};

			Varyings vert(Attributes input) 
			{
				Varyings output;
				
				VertexPositionInputs vertexInput = GetVertexPositionInputs(input.positionOS);
				VertexNormalInputs vertexNormalInput = GetVertexNormalInputs(input.normalOS, input.tangentOS);
				float3 positionWS = vertexInput.positionWS;
				float3 normalWS = vertexNormalInput.normalWS;

				half width = _OutlineWidth * 0.001;
				float2 offset = 0;
				half4 positionCS = vertexInput.positionCS;

			#if defined(_NORMAL_VERTEXCOLORSMOOTH)
				input.color = input.color * 2 - 1;
				float3x3 tbn = float3x3(vertexNormalInput.tangentWS, vertexNormalInput.bitangentWS, vertexNormalInput.normalWS);
				float3 linearRawData = input.color.rgb;
				float3 smoothNormalWS  = mul(linearRawData, tbn);
				float3 smoothNormalCS = mul((float3x3) UNITY_MATRIX_VP, smoothNormalWS);
				offset = normalize(smoothNormalCS.xy) * width * vertexInput.positionCS.w;
				positionCS = vertexInput.positionCS;
				positionCS.xy += offset;
			#else
				float3 normalCS = mul((float3x3) UNITY_MATRIX_VP, vertexNormalInput.normalWS);
				offset = normalize(normalCS.xy) * width * vertexInput.positionCS.w;
				positionCS.xy += offset;
			#endif
				output.positionCS = positionCS;
				output.uv = input.texcoord;
				output.normalVS = TransformWorldToViewDir(vertexNormalInput.normalWS);
				return output;
			}

			half4 frag(Varyings input) : SV_TARGET
			{
				return half4(0,0,0,1);
			}
            ENDHLSL
        }