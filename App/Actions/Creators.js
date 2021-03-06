import Types from './Types'

const receivedUser = (user, settings, location) =>
({ type: Types.USER_RECEIVED, user, settings, location })

const receivedActiveUsers = (users) =>
({ type: Types.ACTIVE_USERS_RECEIVED, users })

const authChange = (username, email, uid, photo) =>
({ type: Types.AUTH_CHANGE, username, email, uid, photo })

const registerAttempt = () =>
({ type: Types.REGISTER_ATTEMPT })

const registerSuccess = () =>
({ type: Types.REGISTER_SUCCESS })

const registerFailure = () =>
({ type: Types.REGISTER_FAILURE })

const loginAttempt = () =>
({ type: Types.LOGIN_ATTEMPT })

const loginSuccess = () =>
({ type: Types.LOGIN_SUCCESS })

const loginFailure = (errorCode) =>
({ type: Types.LOGIN_FAILURE, errorCode })

const logoutAttempt = () =>
({ type: Types.LOGIN_ATTEMPT })

const logoutSuccess = () =>
({ type: Types.LOGIN_SUCCESS })

const logoutFailure = () =>
({ type: Types.LOGIN_FAILURE })

const setActiveCategory = (category) =>
({ type: Types.SET_ACTIVE_CATEGORY })

const receivedAcapellaMessage = (data) =>
({ type: Types.RECEIVED_MSG_AUDIO, data })

const receivedAcapellaError = (error) =>
({ type: Types.RECEIVED_MSG_ERROR, error })

const getAudioMsg = (msg, msgVoice) =>
({ type: Types.GET_MSG_AUDIO, msg, msgVoice })

const startup = () => ({ type: Types.STARTUP })

/**
 Makes available all the action creators we've created.
 */
export default {
  startup,

  receivedUser,
  receivedActiveUsers,
  authChange,

  registerAttempt,
  registerSuccess,
  registerFailure,

  loginAttempt,
  loginFailure,
  loginSuccess,

  logoutAttempt,
  logoutSuccess,
  logoutFailure,

  setActiveCategory,

  getAudioMsg,
  receivedAcapellaMessage,
  receivedAcapellaError
}
